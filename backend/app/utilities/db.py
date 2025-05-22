import mysql.connector
from mysql.connector import connect
from app.config import settings

from mysql.connector import Error

def get_db():
    try:
        return connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
    except Error as e:
        print("Error connecting to the database:", e)
        raise