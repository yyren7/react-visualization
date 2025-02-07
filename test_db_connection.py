import psycopg2

db_host = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
db_port = "5432"
db_name = "postgres"  # Corrected database name to 'postgres'
db_user = "otocolobus"
db_password = "WcM1hCwTVBfm6XnvXm29"

try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    if result and result[0] == 1:
        print("Successfully connected to the database!")
    else:
        print("Failed to connect to the database. Could not execute test query.")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Failed to connect to the database. Error: {e}")