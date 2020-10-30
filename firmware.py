"""
Database Firmware Updates related functions
"""
from typing import List

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
