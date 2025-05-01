-- Tabla de empleados
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,                 -- Id del empleado
    nombres varchar(max),                     -- Nombre y apellido del empleado
    fecha varchar(max),                 -- Fecha y hora de contratación (formato ISO)
    department_id INTEGER,         -- Id del departamento
    job_id INTEGER,							-- Id del puesto
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Tabla de departamentos
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,                 -- Id del departamento
    department varchar(max)                -- Nombre del departamento
);

-- Tabla de puestos de trabajo
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,                 -- Id del puesto
    job varchar(max)                       -- Nombre del puesto
);

--Section 2: SQL


--Number of employees hired for each job and department in 2021 divided by quarter. The
--table must be ordered alphabetically by department and job.

SELECT
    d.department AS department,
    j.job AS job,
    SUM(CASE 
            WHEN TRY_CAST(e.fecha AS DATE) >= '2021-01-01' AND TRY_CAST(e.fecha AS DATE) < '2021-04-01' THEN 1 
            ELSE 0 
        END) AS Q1,
    SUM(CASE 
            WHEN TRY_CAST(e.fecha AS DATE) >= '2021-04-01' AND TRY_CAST(e.fecha AS DATE) < '2021-07-01' THEN 1 
            ELSE 0 
        END) AS Q2,
    SUM(CASE 
            WHEN TRY_CAST(e.fecha AS DATE) >= '2021-07-01' AND TRY_CAST(e.fecha AS DATE) < '2021-10-01' THEN 1 
            ELSE 0 
        END) AS Q3,
    SUM(CASE 
            WHEN TRY_CAST(e.fecha AS DATE) >= '2021-10-01' AND TRY_CAST(e.fecha AS DATE) < '2022-01-01' THEN 1 
            ELSE 0 
        END) AS Q4
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN jobs j ON e.job_id = j.id
WHERE ISDATE(e.fecha) = 1  -- Asegura que solo se consideren fechas válidas
  AND TRY_CAST(e.fecha AS DATE) >= '2021-01-01'
  AND TRY_CAST(e.fecha AS DATE) < '2022-01-01'
GROUP BY d.department, j.job
ORDER BY d.department ASC, j.job ASC;


--List of ids, name and number of employees hired of each department that hired more
--employees than the mean of employees hired in 2021 for all the departments, ordered
--by the number of employees hired (descending).

WITH empleados_por_departamento AS (
    SELECT
        d.id AS department_id,
        d.department AS department_name,
        COUNT(*) AS total_empleados
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE ISDATE(e.fecha) = 1
      AND TRY_CAST(e.fecha AS DATE) >= '2021-01-01'
      AND TRY_CAST(e.fecha AS DATE) < '2022-01-01'
    GROUP BY d.id, d.department
),
media_contrataciones AS (
    SELECT AVG(CAST(total_empleados AS FLOAT)) AS promedio_empleados
    FROM empleados_por_departamento
)
SELECT 
    epd.department_id,
    epd.department_name,
    epd.total_empleados
FROM empleados_por_departamento epd
CROSS JOIN media_contrataciones m
WHERE epd.total_empleados > m.promedio_empleados
ORDER BY epd.total_empleados DESC;

