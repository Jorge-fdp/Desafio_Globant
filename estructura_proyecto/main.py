from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import pandas as pd
import models
import schemas
import io
from database import engine, SessionLocal
from models import Employee,Department,Job

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
        column_names = ["id", "name"]
    elif table_name == "employees":
        column_names = ["id", "nombres", "fecha", "department_id", "job_id"]
    else:
        raise HTTPException(status_code=400, detail="Invalid table name.")

    # Leer el CSV sin encabezados y asignar nombres de columnas
    df = pd.read_csv(file.file, header=None, names=column_names)

    # Filtrar filas sin id (solo para employees si es necesario)
    if table_name == "employees":
        df = df[df["id"].notna()]

    # InsertaInserta los datos en la tabla correspondiente
    if table_name == "departments":
        db.bulk_insert_mappings(models.Department, df.to_dict(orient="records"))
    elif table_name == "jobs":
        db.bulk_insert_mappings(models.Job, df.to_dict(orient="records"))
    elif table_name == "employees":
        db.bulk_insert_mappings(models.Employee, df.to_dict(orient="records"))

    db.commit()
    return {"status": "success", "rows": len(df)}



# Metodo para carga amsiva employees
@app.post("/upload_employees_csv")
async def upload_employees_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Leer CSV sin encabezado
        df = pd.read_csv(file.file, header=None, names=["id", "nombres", "fecha", "department_id", "job_id"], sep=",")

        # Convertir department_id y job_id a numéricos, reemplazar nulos/no numéricos por -1
        df['department_id'] = pd.to_numeric(df['department_id'], errors='coerce').fillna(-1).astype(int)
        df['job_id'] = pd.to_numeric(df['job_id'], errors='coerce').fillna(-1).astype(int)

        # Eliminar registros con nombres o fecha nula
        df = df.dropna(subset=["nombres", "fecha"])

        # Consultar IDs válidos en departments y jobs
        valid_department_ids = {r[0] for r in db.execute(text("SELECT id FROM departments")).fetchall()}
        valid_job_ids = {r[0] for r in db.execute(text("SELECT id FROM jobs")).fetchall()}

        # Filtrar registros con claves foráneas válidas
        df = df[df['department_id'].isin(valid_department_ids)]
        df = df[df['job_id'].isin(valid_job_ids)]

        # Verificar si hay registros válidos
        if df.empty:
            raise HTTPException(status_code=400, detail="No hay registros válidos para insertar.")

        # Dividir en lotes e insertar
        batch_size = 1000
        total_records = len(df)
        batches = [df[i:i + batch_size] for i in range(0, total_records, batch_size)]

        for batch in batches:
            records = batch.to_dict(orient="records")
            try:
                db.bulk_insert_mappings(Employee, records)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                return {"message": f"Error al insertar un lote de empleados: {str(e)}"}

        return {"message": f"Se insertaron {total_records} empleados."}

    except Exception as e:
        return {"message": f"Error al procesar el archivo CSV: {str(e)}"}


# Metodo para carga amsiva departments
@app.post("/upload_departments_csv")
def upload_departments_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file, header=None, names=["id", "department"], sep=",")
    records = df.to_dict(orient="records")
    
    db.bulk_insert_mappings(models.Department, records)
    db.commit()
    return {"message": f"Se insertaron {len(records)} departamentos"}

# Metodo para carga amsiva tabla jobs
@app.post("/upload_jobs_csv")
def upload_jobs_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file, header=None, names=["id", "job"], sep=",")
    records = df.to_dict(orient="records")
    
    db.bulk_insert_mappings(models.Job, records)
    db.commit()
    return {"message": f"Se insertaron {len(records)} jobs"}


