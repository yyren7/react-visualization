import psycopg2

db_host = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
db_port = "5432"
db_name = "postgres"
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

    # 查询数据库中的所有表
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")

        # 查询每个表的前 10 行数据
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()

        for row in rows:
            print(row)

    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    if result and result[0] == 1:
        print("Successfully connected to the database!", flush=True)
    else:
        print("Failed to connect to the database. Could not execute test query.", flush=True)
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Failed to connect to the database. Error: {e}", flush=True)