"""
Database Firmware Updates related functions
"""
from typing import List

from sqlalchemy.engine import result
from sqlalchemy.sql.functions import concat

from . import session
from .models.device import Device
from .models.firmware_update import Update


def get_current_devices() -> List[str]:
    """
    SELECT codename FROM devices WHERE firmware_updater IS TRUE ORDER BY codename
    :return: list of codename strings
    """
    return [i.codename for i in
            session.query(Device.codename).filter(Device.firmware_updater == 1).order_by(Device.codename)]


def update_in_db(codename, version) -> bool:
    """
    Check if an update is already in the database
    :param codename: Update codename
    :param version: Update version
    :return: True if the update is already in the database
    """
    return bool(session.query(Update).filter_by(codename=codename).filter_by(version=version).count() >= 1)


def get_all_updates() -> result:
    """
    SELECT CONCAT(d.name, ' ', d.region) as name, firmware.codename, version,
           android, branch, filename, size, md5, date
    from firmware
             JOIN devices d on firmware.codename = d.codename
    GROUP BY md5
    :return: list of firmware results
    """
    return session.query(
        concat(Device.name, ' ', Device.region).label('name'), Update.codename, Update.version,
        Update.android, Update.branch, Update.filename, Update.size, Update.md5, Update.date
    ).join(Device, Update.codename == Device.codename).group_by(Update.md5).all()
