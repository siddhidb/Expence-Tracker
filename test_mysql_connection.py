import os
import mysql.connector
from dotenv import load_dotenv

def test_mysql_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database credentials
        config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'raise_on_warnings': True
        }
        
        print("Attempting to connect to MySQL with the following settings:")
        print(f"Host: {config['host']}")
        print(f"User: {config['user']}")
        print(f"Database: {config['database']}")
        
        # Try to connect
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"\nSuccessfully connected to MySQL Server version {db_info}")
            
            # Create a cursor
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            
            # Check if tables exist
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("\nExisting tables:")
            for table in tables:
                print(f"- {table[0]}")
            
            cursor.close()
            connection.close()
            print("\nConnection closed.")
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if err.errno == 2003:
            print("\nCommon causes:")
            print("1. MySQL server is not running")
            print("2. Incorrect host or port")
            print("3. Firewall blocking the connection")
        elif err.errno == 1045:
            print("\nCommon causes:")
            print("1. Incorrect username or password")
            print("2. User doesn't have permission to access the database")
        elif err.errno == 1049:
            print("\nCommon causes:")
            print("1. Database doesn't exist")
            print("2. Typo in the database name")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_mysql_connection()
