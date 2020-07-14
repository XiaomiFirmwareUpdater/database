"""MIUI Updates Tracker Database Device model"""
from sqlalchemy import Column, INT, VARCHAR, Table, TEXT, BOOLEAN

from . import Base


class Device(Base):
    """
    Update class that represents a device update
    """
    __tablename__ = 'devices'
    id: int = Column(INT(), primary_key=True, autoincrement=True, nullable=False)
    name: str = Column(VARCHAR(40))
    codename: str = Column(VARCHAR(30), nullable=False)
    region: str = Column(VARCHAR(30))
    miui_name: str = Column(VARCHAR(30))
    miui_code: str = Column(VARCHAR(6))
    mi_website_id: int = Column(INT())
    picture: str = Column(TEXT())
    eol: bool = Column(BOOLEAN(), default=False)

    def __repr__(self):
        return f"<Device(codename={self.codename}, name={self.name}, region={self.region})>"


def get_table(metadata):
    return Table('devices', metadata,
                 Column('id', INT(), primary_key=True, autoincrement=True, nullable=False),
                 Column('name', VARCHAR(40), nullable=False),
                 Column('codename', VARCHAR(30), nullable=False, index=True, onupdate="CASCADE"),
                 Column('region', VARCHAR(30), nullable=False),
                 Column('miui_name', VARCHAR(30), nullable=False),
                 Column('miui_code', VARCHAR(6), nullable=False),
                 Column('mi_website_id', INT(), nullable=True),
                 Column('picture', TEXT(), nullable=True),
                 Column('eol', BOOLEAN(), default=False, nullable=False),
                 )
