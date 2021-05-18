"""MIUI Updates Tracker Database initialization"""
import logging
from pathlib import Path

import yaml
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder

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
metadata.create_all(engine)

Session: sessionmaker = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

latest_updates = Table("latest_updates", metadata, autoload=True, autoload_with=engine)
latest_firmware = Table("latest_firmware", metadata, autoload=True, autoload_with=engine)


def close_db():
    connection.close()
    engine.dispose()
    if tunnel:
        tunnel.stop()
