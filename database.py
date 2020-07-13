"""
Database related functions
"""
from typing import Union, Tuple, List, Optional

from sqlalchemy.engine import result
from sqlalchemy.sql.functions import concat, func

from miui_updates_tracker.common.database import session
from miui_updates_tracker.common.database.models.device import Device
from miui_updates_tracker.common.database.models.update import Update


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
                 AND updates.method = "Recovery"
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
        Update.branch == branch).filter(Update.method == "Recovery").filter(
        Update.type == "Full").order_by(Update.date.desc()).limit(99999).subquery()
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
    AND devices.eol = 0
    AND devices.miui_code != ""
    AND LENGTH(devices.miui_code) = 4
    """
    all_latest = session.query(
        Update.codename, Update.version, Update.android, Update.branch,
        Update.method, Update.size, Update.md5, Update.link, Update.changelog, Update.date).filter(
        Update.branch == branch).filter(Update.type == "Full").order_by(Update.date.desc()).limit(99999).subquery()
    latest = session.query(all_latest).group_by(all_latest.c.codename).group_by(all_latest.c.method).subquery()
    updates = session.query(Device.name, concat(Device.name, ' ', Device.region).label('fullname'), latest).filter(
        latest.c.codename == Device.codename).filter(Device.eol == '0').filter(
        Device.miui_code != "").filter(func.length(Device.miui_code) == 4).all()
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


def get_recovery_update(version) -> Update:
    """
    Get an update from the database
    :param version: update version
    :return: update object
    """
    return session.query(Update).filter(Update.version == version).filter(
        Update.method == "Recovery").filter(Update.type == "Full").first()


def device_in_db(codename) -> bool:
    """
    Check if a device is already in the database
    :param codename: Device codename
    :return: True if the update is already in the database
    """
    return bool(session.query(Device).filter_by(codename=codename).count() >= 1)
