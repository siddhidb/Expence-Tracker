import mysql.connector

def try_connect(password, auth_plugin=None):
    try:
        conn_params = {
            'host': 'localhost',
            'user': 'root',
            'password': password
        }
        if auth_plugin:
            conn_params['auth_plugin'] = auth_plugin
            
        conn = mysql.connector.connect(**conn_params)
        print(f"\nSuccessfully connected to MySQL! (using auth_plugin={auth_plugin or 'default'})")
        
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES;")
        print("\nDatabases:")
        for db in cursor:
            print(f"- {db[0]}")
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"\nFailed to connect (auth_plugin={auth_plugin or 'default'}): {err}")
        return False

# Try different combinations
print("Testing MySQL connection with different settings...")

# Try with empty password
try_connect("", None)

# Try with 'siddhi' password
try_connect("siddhi", None)

# Try with 'root' password
try_connect("root", None)

# Try with no password and native auth
try_connect("", 'mysql_native_password')

# Try with 'siddhi' and native auth
try_connect("siddhi", 'mysql_native_password')

# Try with 'root' and native auth
try_connect("root", 'mysql_native_password')
