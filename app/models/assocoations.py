from sqlalchemy import Table, Column, ForeignKey
from app.db.base_class import Base


# Lab classes associations
LabAssignment = Table(
    'lab_assignments',
    Base.metadata,
    Column('class_id', ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)