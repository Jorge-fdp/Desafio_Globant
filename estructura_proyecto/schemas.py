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
    job_id: int
    department_id: int
