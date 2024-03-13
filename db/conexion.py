from functools import wraps
from flask import g
import psycopg2
import os
from dotenv import load_dotenv
import functools

# Conexión a la base de datos PostgreSQL
def conect():
    # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # Acceder a las variables de entorno
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
        print("Conexión a la base de datos exitosa.")
        return conn

def create_tables(conn):
    try:
        cursor = conn.cursor()

        # Crear la tabla 'usuario' si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                cc int,
                email VARCHAR(100)
            )
        """)
        print("Tabla 'users' creada correctamente.")

        # Crear la tabla 'tarea' si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id_task SERIAL PRIMARY KEY,
                title VARCHAR(255),
                description TEXT,
                status VARCHAR(20),
                due_date DATE,
                user_id SERIAL REFERENCES users(user_id),
                crate_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Tabla 'tasks' creada correctamente.")

        conn.commit()
        print("Operaciones de creación completadas.")
    except psycopg2.Error as e:
        print("Error al crear las tablas:", e)

# Decorador para conectar a la base de datos antes de ejecutar la vista
def connect_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'conn'):
            g.conn = conect()  # Establecer la conexión a la base de datos en el contexto global
        try:
            result = func(*args, **kwargs)  # Ejecutar la función de vista
            g.conn.commit()  # Confirmar los cambios en la base de datos
            return result
        except psycopg2.Error as e:
            # Manejar cualquier error que ocurra durante la ejecución de la vista
            print("Error al ejecutar la vista:", e)
            return {'mensaje': 'Error de base de datos'}, 500
        finally:
            # Cerrar la conexión a la base de datos después de que la vista haya terminado
            if hasattr(g, 'conn'):
                g.conn.close()
                delattr(g, 'conn')
    return wrapper

