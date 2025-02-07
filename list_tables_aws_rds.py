import psycopg2

db_host = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
db_port = "5432"
db_name = "postgres"  # Using 'postgres' database to list tables
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
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()

    if tables:
        print("Tables in your AWS RDS database:")
        for table in tables:
            print(table[0])
    else:
        print("No tables found in your AWS RDS database.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Failed to connect to the database or list tables. Error: {e}")