from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

# Reemplaza con el nombre de tu servidor y base de datos
server = "localhost\\SQLEXPRESSJDP"  # o solo "localhost" si es la instancia por defecto
database_name = "desafio_globant"

# Cadena con autenticación integrada (Windows Authentication)
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database_name};"
    f"Trusted_Connection=yes;"
)

params = urllib.parse.quote_plus(connection_string)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
