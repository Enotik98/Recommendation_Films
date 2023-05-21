import psycopg2

def connect_to_database():
    conn = psycopg2.connect(
        host="localhost",
        database="Movies",
        user="postgres",
        password="16"
    )
    return conn

def execute_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result