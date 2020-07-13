"""MIUI Updates Tracker Database initialization"""
import logging

from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker

from miui_updates_tracker import CONFIG
from miui_updates_tracker.common.database.models.update import get_table as update_table
from miui_updates_tracker.common.database.models.device import get_table as device_table

logger = logging.getLogger(__name__)
engine: Engine = create_engine(CONFIG.get('connection_string'))
logger.info(f"Connected to {engine.name} database at {engine.url}")
connection: Connection = engine.connect()
connection.execute('SET GLOBAL connect_timeout=6000')

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
    update_table(metadata)
    metadata.create_all(engine)

Session: sessionmaker = sessionmaker(bind=engine)
session = Session()
