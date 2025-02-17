import psycopg2

# Database connection details (from test_connection.py)
DB_HOST = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
DB_NAME = "ocotolobus"  # Changed DB_NAME to "ocotolobus"
DB_USER = "otocolobus"
DB_PASSWORD = "WcM1hCwTVBfm6XnvXm29"
DB_PORT = 5432

def apply_database_migration():
    """Applies database migration to remove userid from messages table."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()

        # SQL commands to drop foreign key constraint and column
        sql_commands = [
            "ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_user_id_fkey;",
            "ALTER TABLE messages DROP COLUMN IF EXISTS user_id;"
        ]

        for command in sql_commands:
            cursor.execute(command)
            print(f"Executed SQL command: {command}")

        conn.commit()
        print("Database migration applied successfully!")
        return True

    except psycopg2.Error as e:
        print(f"Database migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    apply_database_migration()
