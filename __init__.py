"""MIUI Updates Tracker Database initialization"""
import logging
from pathlib import Path

import yaml
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder

from .models.device import get_table as device_table
from .models.firmware_update import get_table as firmware_updates_table
from .models.miui_update import get_table as miui_updates_table

logger = logging.getLogger(__name__)
logging.getLogger('sshtunnel.SSHTunnelForwarder').setLevel(logging.ERROR)
logging.getLogger('paramiko.transport').setLevel(logging.ERROR)
module_path = Path(__file__).parent
tunnel = None
# read db configuration file
with open(module_path / 'config.yml', 'r') as f:
    db_config = yaml.load(f, Loader=yaml.FullLoader)
if db_config.get('local_db') is True:
    engine: Engine = create_engine(db_config.get('local_connection_string'), pool_recycle=3600, pool_pre_ping=True)
else:
    tunnel = SSHTunnelForwarder(
        (db_config.get('db_server'), 22),
        ssh_username=db_config.get('ssh_username'), ssh_pkey=db_config.get('ssh_key'),
        remote_bind_address=('127.0.0.1', db_config.get('db_port'))
    )
    tunnel.daemon_forward_servers = True
    tunnel.start()
    connection_string = db_config.get('db_connection_string').replace(
        '$host', tunnel.local_bind_host).replace('$port', str(tunnel.local_bind_port))
    engine: Engine = create_engine(connection_string, pool_recycle=3600, pool_pre_ping=True)
logger.info(f"Connected to {engine.name} database at {engine.url}")
connection: Connection = engine.connect()
# connection.execute('SET GLOBAL connect_timeout=6000')

# Create a MetaData instance
metadata: MetaData = MetaData()
# reflect db schema to MetaData
metadata.reflect(bind=engine)
# check if the table exists
ins = inspect(engine)
if 'devices' not in ins.get_table_names():
    logger.info("Devices table not found, creating one")
    device_table(metadata)
    metadata.create_all(engine)
if 'updates' not in ins.get_table_names():
    logger.info("Updates table not found, creating one")
    miui_updates_table(metadata)
    metadata.create_all(engine)
if 'firmware' not in ins.get_table_names():
    logger.info("Firmware table not found, creating one")
    firmware_updates_table(metadata)
    metadata.create_all(engine)

Session: sessionmaker = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()


def close_db():
    connection.close()
    engine.dispose()
    if tunnel:
        tunnel.stop()
