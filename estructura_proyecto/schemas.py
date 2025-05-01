from pydantic import BaseModel

class DepartmentsBase(BaseModel):
    id: int
    department: str

class JobBase(BaseModel):
    id: int
    job: str

class EmployeeBase(BaseModel):
    id: int
    nombres: str
    fecha: str
    department_id: int
    job_id: int

