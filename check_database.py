import psycopg2
from psycopg2 import OperationalError

def test_database_connection():
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(
            host="dpg-ctnuipdsvqrc73b4c260-a.frankfurt-postgres.render.com",
            database="cartoondatabase",
            user="cartoondatabase_user",
            password="VeniS20ArXFHvmN3L1xLCDL1yE8vn2E6",
            port=5432  # Default port for PostgreSQL
        )
        
        print("Successfully connected to the database")
        
        # Optional: Test a query
        cursor = connection.cursor()
        cursor.execute("SELECT version();")  # Fetch PostgreSQL server version
        db_version = cursor.fetchone()
        print("PostgreSQL server version:", db_version)
        
    except OperationalError as e:
        print("Error while connecting to the database:", e)
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Database connection closed")

# Run the function
test_database_connection()
