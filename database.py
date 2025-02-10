import mysql.connector

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        sentence_count INT DEFAULT 0
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        sentence TEXT NOT NULL,
        elapsed_time FLOAT NOT NULL,
        correct_chars INT NOT NULL,
        total_chars INT NOT NULL
    );
    """)

def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="June",
        database="typing_speed"
    )
    cursor = connection.cursor()
    create_tables(cursor)
    return connection, cursor
