import psycopg2

host = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
database = "postgres"
user = "otocolobus"
password = "WcM1hCwTVBfm6XnvXm29"
port = 5432

try:
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
    print("Connection successful!")
    conn.close()

except psycopg2.Error as e:
    print(f"Connection failed: {e}")