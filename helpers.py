"""
Database helper functions
"""
from humanize import naturalsize

from miui_updates_tracker import WORK_DIR
from miui_updates_tracker.common.database.database import get_latest_updates
from miui_updates_tracker.utils.data_manager import DataManager


def export_latest():
    """
    Export latest updates from the database to YAML file
    :return:
    """
    latest_updates = get_latest_updates() + get_latest_updates(branch="Weekly")
    latest = [{
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
    DataManager.write_file(f"{WORK_DIR}/data/latest.yml", latest)
