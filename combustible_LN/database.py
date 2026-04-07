"""
MÓDULO DE CONEXIÓN A BASE DE DATOS
Sistema de Control de Combustible - Municipio de Caranavi
"""

import mysql.connector
import pandas as pd


DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",           
    "database": "caranavi",
    "charset":  "utf8mb4"
}


def get_connection():
    """Retorna una conexión activa a MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


def query_to_df(sql: str, params=None) -> pd.DataFrame:
    """Ejecuta una consulta SQL y retorna un DataFrame de pandas."""
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql(sql, conn, params=params)
        return df
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        print(f"   SQL: {sql}")
        print(f"   Params: {params}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
