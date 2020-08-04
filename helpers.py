"""
Database helper functions
"""
from humanize import naturalsize

from .database import get_devices, get_all_latest_updates


def export_latest():
    """
    Export latest updates from the database to YAML file
    :return:
    """
    latest_updates = get_all_latest_updates()
    return [{
        "android": item.android,
        "branch": item.branch,
        "codename": item.codename,
        "date": item.date,
        "name": item.fullname,
        "md5": item.md5,
        "method": item.method,
        "link": item.link,
        "size": naturalsize(item.size),
        "version": item.version
    } for item in latest_updates]


def export_devices():
    devices = get_devices()
    return {device.codename: [device.name, device.miui_name] for device in devices}
