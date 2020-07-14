"""
Database helper functions
"""
from humanize import naturalsize

from .database import get_latest_updates


def export_latest():
    """
    Export latest updates from the database to YAML file
    :return:
    """
    latest_updates = get_latest_updates() + get_latest_updates(branch="Weekly")
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
