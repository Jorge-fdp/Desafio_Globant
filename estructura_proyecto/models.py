from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger
from database import Base  # sin punto


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=False)
    department = Column(String)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=False)
    job = Column(String(100), unique=True, nullable=False)

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=False)
    nombres = Column(String)
    fecha = Column(String)
    department_id = Column(Integer)
    job_id = Column(SmallInteger)  # <- Aquí podría estar el problema
