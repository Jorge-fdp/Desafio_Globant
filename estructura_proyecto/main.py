from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import models
import schemas
import io
from database import engine, SessionLocal
from models import Department,Job

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload_csv/{table_name}")
async def upload_csv(table_name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    # Define headers según el nombre de la tabla
    if table_name == "departments":
        column_names = ["id", "name"]
    elif table_name == "jobs":
        column_names = ["id", "name", "department_id"]
    elif table_name == "employees":
        column_names = ["id", "nombres", "fecha", "department_id", "job_id"]
    else:
        raise HTTPException(status_code=400, detail="Invalid table name.")

    # Leer el CSV sin encabezados y asignar nombres de columnas
    df = pd.read_csv(file.file, header=None, names=column_names)

    # Filtrar filas sin id (solo para employees si es necesario)
    if table_name == "employees":
        df = df[df["id"].notna()]

    # Insertar en la tabla correspondiente
    if table_name == "departments":
        db.bulk_insert_mappings(models.Department, df.to_dict(orient="records"))
    elif table_name == "jobs":
        db.bulk_insert_mappings(models.Job, df.to_dict(orient="records"))
    elif table_name == "employees":
        db.bulk_insert_mappings(models.Employee, df.to_dict(orient="records"))

    db.commit()
    return {"status": "success", "rows": len(df)}



@app.post("/batch_insert/employees")
def batch_insert_employees(employees: list[schemas.EmployeeBase], db: Session = Depends(get_db)):
    if not 1 <= len(employees) <= 1000:
        raise HTTPException(status_code=400, detail="Batch size must be between 1 and 1000.")

    # Opcional: filtrar los que tengan id = None
    valid_employees = [e.dict() for e in employees if e.id is not None]

    db.bulk_insert_mappings(models.Employee, valid_employees)
    db.commit()
    return {"status": "batch inserted", "count": len(valid_employees)}

@app.post("/upload_departments_csv")
def upload_departments_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file, header=None, names=["id", "department"], sep=",")
    records = df.to_dict(orient="records")
    
    db.bulk_insert_mappings(models.Department, records)
    db.commit()
    return {"message": f"Se insertaron {len(records)} departamentos"}

@app.post("/upload_jobs_csv")
def upload_jobs_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file, header=None, names=["id", "job"], sep=",")
    records = df.to_dict(orient="records")
    
    db.bulk_insert_mappings(models.Job, records)
    db.commit()
    return {"message": f"Se insertaron {len(records)} jobs"}


