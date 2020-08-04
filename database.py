"""
Database related functions
"""
from typing import Union, Optional

from sqlalchemy import or_
from sqlalchemy.engine import result
from sqlalchemy.sql.functions import concat, func

from . import session
from .models.device import Device
from .models.update import Update


def get_mi_website_ids() -> result:
    """
    SELECT mi_website_id as id, region FROM devices WHERE mi_website_id IS NOT NULL AND eol != 1 GROUP BY mi_website_id
    :return: list of tuples of (id, region)
    """
    return session.query(Device.mi_website_id, Device.region).filter(Device.mi_website_id != None).filter(
        Device.eol != 1).group_by(Device.mi_website_id)


def get_fastboot_codenames() -> result:
    """
    SELECT codename, region FROM devices WHERE mi_website_id IS NOT NULL AND eol != 1 ORDER BY codename
    :return: list of codenames
    """
    return session.query(Device.codename, Device.region).filter(Device.mi_website_id != None).filter(
        Device.eol != 1).order_by(Device.codename).all()


def get_current_devices() -> result:
    """
    SELECT codename from devices WHERE eol = 0 AND miui_code != "" AND LENGTH(miui_code) = 4
    :return: list of codenames
    """
    return session.query(
        Device.codename).filter(Device.eol == "0").filter(Device.miui_code != "").filter(
        func.length(Device.miui_code) == 4).all()


def get_devices() -> result:
    """
    SELECT codename, CONCAT(name, ' ', region) as name, miui_name
    from devices
    WHERE miui_code != ""
      AND LENGTH(miui_code) = 4
    GROUP BY codename
    ORDER BY codename
    """
    return session.query(
        Device.codename, concat(Device.name, ' ', Device.region).label('name'), Device.miui_name
    ).filter(Device.miui_code != "").filter(func.length(Device.miui_code) == 4).order_by(Device.codename).all()


def get_device_latest_version(codename) -> result:
    """
    SELECT codename, version, android from updates WHERE codename = 'codename' AND updates.branch = "Stable" AND updates.type = "Full" ORDER BY date DESC LIMIT 1
    :param codename: device codename
    :return: codename, version, android object
    """
    return session.query(Update.codename, Update.version, Update.android).filter(Update.codename == codename).filter(
        Update.branch == "Stable").filter(Update.type == "Full").order_by(Update.date.desc()).limit(1).first()


def get_latest_versions(branch: str = "Stable") -> result:
    """
    SELECT latest.*
    FROM devices,
     (
         SELECT all_latest.*
         FROM (SELECT codename, version, android
               from updates
               WHERE updates.branch = "Stable"
                 AND updates.type = "Full"
               ORDER BY updates.date DESC
               LIMIT 99999) as all_latest
         GROUP BY all_latest.codename) as latest
    WHERE latest.codename = devices.codename
    AND devices.eol = 0
    AND devices.miui_code != ""
    AND LENGTH(devices.miui_code) = 4
    """
    all_latest = session.query(Update.codename, Update.version, Update.android).filter(
        Update.branch == branch).filter(Update.type == "Full").order_by(Update.date.desc()).limit(99999).subquery()
    latest = session.query(all_latest).group_by(all_latest.c.codename).subquery()
    updates = session.query(latest).filter(latest.c.codename == Device.codename).filter(
        Device.eol == '0').filter(Device.miui_code != "").filter(func.length(Device.miui_code) == 4).all()
    return updates


def get_latest_updates(branch: str = "Stable") -> result:
    """
     SELECT CONCAT(devices.name, ' ', devices.region) as name, latest.*
    FROM devices,
     (
         SELECT all_latest.*
         FROM (SELECT codename, version, branch, method, size, md5, link, changelog, date
               from updates
               WHERE updates.branch = "Stable"
                 AND updates.type = "Full"
               ORDER BY updates.date DESC
               LIMIT 99999) as all_latest
         GROUP BY all_latest.codename, all_latest.method) as latest
    WHERE latest.codename = devices.codename
    AND devices.miui_code != ""
    AND LENGTH(devices.miui_code) = 4
    ORDER BY date desc
    """
    all_latest = session.query(
        Update.codename, Update.version, Update.android, Update.branch,
        Update.method, Update.size, Update.md5, Update.link, Update.changelog, Update.date).filter(
        Update.branch == branch).filter(Update.type == "Full").order_by(Update.date.desc()).limit(99999).subquery()
    latest = session.query(all_latest).group_by(all_latest.c.codename).group_by(all_latest.c.method).subquery()
    updates = session.query(Device.name, concat(Device.name, ' ', Device.region).label('fullname'), latest).filter(
        latest.c.codename == Device.codename).filter(Device.miui_code != "").filter(
        func.length(Device.miui_code) == 4).order_by(latest.c.date.desc()).all()
    return updates


def get_all_latest_updates():
    return get_latest_updates() + get_latest_updates(branch="Stable Beta") + get_latest_updates(
        branch="Weekly")


def get_device_latest(codename) -> result:
    """
    SELECT CONCAT(devices.name, ' ', devices.region) as name, latest.*
    FROM devices,
         (
             SELECT all_latest.*
             FROM (SELECT codename, version, android, branch, method, size, md5, link, changelog, date
                   from updates
                   WHERE codename like 'whyred%'
                     AND (updates.branch like "Stable%" OR updates.branch = "Weekly")
                     AND updates.type = "Full"
                   ORDER BY updates.date DESC
                   LIMIT 99999) as all_latest
             GROUP BY all_latest.codename, all_latest.method, all_latest.branch) as latest
    WHERE devices.codename = latest.codename
      AND LENGTH(devices.miui_code) = 4
    """
    all_latest = session.query(
        Update.codename, Update.version, Update.android, Update.branch,
        Update.method, Update.size, Update.md5, Update.link, Update.changelog, Update.date).filter(
        Update.codename.startswith(codename)).filter(
        or_(Update.branch.startswith("Stable"), Update.branch == "Weekly")).filter(
        Update.type == "Full").order_by(Update.date.desc()).limit(99999).subquery()
    latest = session.query(all_latest).group_by(all_latest.c.codename).group_by(
        all_latest.c.method).group_by(all_latest.c.branch).subquery()
    updates = session.query(concat(Device.name, ' ', Device.region).label('name'), latest).filter(
        Device.codename == latest.c.codename).filter(func.length(Device.miui_code) == 4).all()
    return updates


def get_device_roms(codename) -> result:
    """
    SELECT CONCAT(devices.name, ' ', devices.region) as name, all_updates.*
    FROM devices,
         (
             SELECT codename, version, android, branch, method, size, md5, link, changelog, date
             from updates
             WHERE codename like 'whyred%'
               AND (updates.branch like "Stable%" OR updates.branch = "Weekly")
               AND updates.type = "Full"
             ORDER BY updates.date DESC
             LIMIT 99999) as all_updates
    WHERE devices.codename = all_updates.codename
      AND LENGTH(devices.miui_code) = 4
    """
    all_updates = session.query(
        Update.codename, Update.version, Update.android, Update.branch, Update.method, Update.size, Update.md5,
        Update.link, Update.changelog, Update.date).filter(
        Update.codename.startswith(codename)).filter(
        or_(Update.branch.startswith("Stable"), Update.branch == "Weekly")).filter(
        Update.type == "Full").order_by(Update.date.desc()).limit(99999).subquery()
    updates = session.query(concat(Device.name, ' ', Device.region).label('name'), all_updates).filter(
        Device.codename == all_updates.c.codename).filter(func.length(Device.miui_code) == 4).all()
    return updates


def get_codename(miui_name) -> result:
    codename = session.query(Device).filter(Device.miui_name == miui_name).first()
    return codename.codename if codename else None


def get_full_name(codename: str) -> Optional[str]:
    full_name = session.query(concat(Device.name, ' ', Device.region)).filter(Device.codename == codename).first()
    return full_name[0] if full_name else None


def get_device_name(codename: str) -> Optional[str]:
    name = session.query(Device.name).filter(Device.codename == codename).first()
    return name[0] if name else None


def get_incremental(version: str) -> Update:
    """
    Get incremental update information of a version
    :type version: str
    :param version: Xiaomi software version
    """
    return session.query(Update).filter(
        Update.version == version).filter(Update.type == "Incremental").first()


def get_version(codename: str, branch: str) -> str:
    """
    Get device version example
    :param codename: device codename
    :type codename: str
    :param branch: Update branch
    """
    query = session.query(Update).filter(Update.codename == codename).filter(Update.branch == branch).first()
    return query.version if query else None


def add_to_db(update: Union[Update, Device], exists=False):
    """Adds an update to the database"""
    if not exists:
        session.add(update)
    session.commit()


def update_in_db(filename) -> bool:
    """
    Check if an update is already in the database
    :param filename: Update file name
    :return: True if the update is already in the database
    """
    return bool(session.query(Update).filter_by(filename=filename).count() >= 1)


def get_update(filename) -> Update:
    """
    Get an update from the database
    :param filename: update filename
    :return: update object
    """
    return session.query(Update).filter(Update.filename == filename).first()


def get_update_by_version(version, method: str = "Recovery") -> Update:
    """
    Get a recovery update from the database
    :param method: Recovery/Fastboot
    :param version: update version
    :return: update object
    """
    return session.query(Update).filter(Update.version == version).filter(
        Update.method == method).filter(Update.type == "Full").first()


def device_in_db(codename) -> bool:
    """
    Check if a device is already in the database
    :param codename: Device codename
    :return: True if the update is already in the database
    """
    return bool(session.query(Device).filter_by(codename=codename).count() >= 1)


def update_stable_beta(recovery_update: Update):
    """
    recovery_update: Update object
    """
    if recovery_update:
        if recovery_update.branch == "Stable Beta":
            recovery_update.branch = "Stable"
            commit_changes()


def commit_changes():
    """
    commit database changes
    """
    session.commit()
