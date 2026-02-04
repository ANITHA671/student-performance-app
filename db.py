import mysql.connector
from mysql.connector import Error

DB_NAME = "student_db"

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="student_user",    # your MySQL username
            password="12345678",    # your MySQL password
            database=DB_NAME
        )
        # Ensure table exists
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            gender VARCHAR(10),
            math_score INT,
            reading_score INT,
            writing_score INT,
            average_score FLOAT,
            grade VARCHAR(2),
            pass_fail VARCHAR(10)
        )
        """)
        cursor.close()
        return conn
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None
