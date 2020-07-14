"""MIUI Updates Tracker Database Update model"""
from sqlalchemy import Column, INT, VARCHAR, CHAR, BIGINT, DATE, TIMESTAMP, ForeignKeyConstraint, Table, TEXT
from sqlalchemy.sql.functions import current_timestamp

from . import Base


class Update(Base):
    """
    Update class that represents a device update
    """
    __tablename__ = 'updates'
    id: int = Column(INT(), primary_key=True, autoincrement=True)
    codename: str = Column(VARCHAR(30), nullable=False)
    version: str = Column(VARCHAR(20), nullable=False)
    android: str = Column(VARCHAR(5), nullable=False)
    branch: str = Column(VARCHAR(6), nullable=False)
    type: str = Column(VARCHAR(11), nullable=False)
    method: str = Column(VARCHAR(8), nullable=False)
    size: str = Column(BIGINT(), nullable=True)
    md5: str = Column(CHAR(32), unique=True, nullable=True)
    filename: str = Column(TEXT(), unique=True, nullable=True)
    link: str = Column(TEXT(), nullable=False)
    changelog: str = Column(TEXT(), nullable=True, default='Bug fixes and system optimizations.')
    date: str = Column(DATE(), nullable=True)
    inserted_on: str = Column(TIMESTAMP(), default=current_timestamp())

    def __repr__(self):
        return f"<Update(codename={self.codename}, version={self.version}, branch={self.branch}, method={self.method})>"

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})


def get_table(metadata):
    return Table('updates', metadata,
                 Column('id', INT(), primary_key=True, autoincrement=True),
                 Column('codename', VARCHAR(30), nullable=False),
                 Column('version', VARCHAR(20), nullable=False),
                 Column('android', VARCHAR(5), nullable=False),
                 Column('branch', VARCHAR(6), nullable=False),
                 Column('type', VARCHAR(11), nullable=False),
                 Column('method', VARCHAR(8), nullable=False),
                 Column('size', BIGINT(), nullable=True),
                 Column('md5', CHAR(32), nullable=True, unique=True),
                 Column('filename', TEXT(), nullable=False, unique=True),
                 Column('link', TEXT(), nullable=False),
                 Column('changelog', TEXT(), nullable=True, default='Bug fixes and system optimizations.'),
                 Column('date', DATE(), nullable=True),
                 Column('inserted_on', TIMESTAMP(), default=current_timestamp()),
                 ForeignKeyConstraint(['codename'], ['devices.codename']))
