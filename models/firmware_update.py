"""XM Firmware Updater Database Update model"""
from sqlalchemy import Column, INT, VARCHAR, CHAR, BIGINT, DATE, TIMESTAMP, ForeignKeyConstraint, Table, TEXT
from sqlalchemy.sql.functions import current_timestamp

from . import Base


class Update(Base):
    """
    Update class that represents a device update
    """
    __tablename__ = 'firmware'
    id: int = Column(INT(), primary_key=True, autoincrement=True)
    codename: str = Column(VARCHAR(30), nullable=False)
    version: str = Column(VARCHAR(20), nullable=False)
    android: str = Column(VARCHAR(5), nullable=False)
    branch: str = Column(VARCHAR(15), nullable=False)
    size: str = Column(BIGINT(), nullable=True)
    md5: str = Column(CHAR(32), unique=True, nullable=True)
    filename: str = Column(TEXT(), unique=True, nullable=True)
    github_link: str = Column(TEXT(), nullable=False)
    osdn_link: str = Column(TEXT(), nullable=True)
    date: str = Column(DATE(), nullable=True)
    inserted_on: str = Column(TIMESTAMP(), default=current_timestamp())

    def __repr__(self):
        return f"<Update(codename={self.codename}, version={self.version}, branch={self.branch})>"

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})


def get_table(metadata):
    return Table('firmware', metadata,
                 Column('id', INT(), primary_key=True, autoincrement=True),
                 Column('codename', VARCHAR(30), nullable=False),
                 Column('version', VARCHAR(20), nullable=False),
                 Column('android', VARCHAR(5), nullable=False),
                 Column('branch', VARCHAR(15), nullable=False),
                 Column('size', BIGINT(), nullable=True),
                 Column('md5', CHAR(32), nullable=True, unique=True),
                 Column('filename', TEXT(), nullable=False, unique=True),
                 Column('github_link', TEXT(), nullable=False),
                 Column('osdn_link', TEXT(), nullable=True),
                 Column('date', DATE(), nullable=True),
                 Column('inserted_on', TIMESTAMP(), default=current_timestamp()),
                 ForeignKeyConstraint(['codename'], ['devices.codename'], use_alter=True))
