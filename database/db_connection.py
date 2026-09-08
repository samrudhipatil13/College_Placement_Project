import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Creates and returns a connection to the MySQL database.
    Returns None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="SAMRUDHI",   # replace with your actual MySQL root password
            database="placement_system"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None