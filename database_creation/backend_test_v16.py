import psycopg2
import uuid
import datetime
import json

# Database connection details - Replace with your actual credentials
DB_HOST = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "otocolobus"
DB_PASSWORD = "WcM1hCwTVBfm6XnvXm29"
DB_PORT = 5432

def connect_db():
    """Establishes a database connection."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def test_crud_operations():
    """Tests CRUD operations for all tables."""
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # --- Users Table CRUD ---
        print("Testing Users table CRUD...")
        user_id = uuid.uuid4()
        created_at = datetime.datetime.now(datetime.timezone.utc)

        # Create
        cursor.execute(
            "INSERT INTO users (user_id, username, email, created_at) VALUES (%s, %s, %s, %s)",
            (str(user_id), "testuser", "test@example.com", created_at)
        )
        # Read
        cursor.execute("SELECT username, email FROM users WHERE user_id = %s", (str(user_id),))
        user_data = cursor.fetchone()
        assert user_data is not None and user_data[0] == "testuser"

        # --- Flowcharts Table CRUD ---
        print("Testing Flowcharts table CRUD...")
        flowchart_id = uuid.uuid4()
        creator_user_id = user_id # Assuming user_id from previous step exists
        created_at = datetime.datetime.now(datetime.timezone.utc)

        # Create
        cursor.execute(
            "INSERT INTO flowcharts (flowchart_id, creator_user_id, flowchart_name, created_at) VALUES (%s, %s, %s, %s)",
            (str(flowchart_id), str(creator_user_id), "Test Flowchart", created_at)
        )
        # Read
        cursor.execute("SELECT flowchart_name FROM flowcharts WHERE flowchart_id = %s", (str(flowchart_id),))
        flowchart_data = cursor.fetchone()
        assert flowchart_data is not None and flowchart_data[0] == "Test Flowchart"

        # --- Flowchart Versions Table CRUD ---
        print("Testing Flowchart Versions table CRUD...")
        version_id = uuid.uuid4()
        created_at = datetime.datetime.now(datetime.timezone.utc)
        nodes_json = json.dumps([{"node_id": str(uuid.uuid4()), "node_type": "start"}])
        edges_json = json.dumps([])

        # Create
        cursor.execute(
            "INSERT INTO flowchart_versions (version_id, flowchart_id, version_number, nodes_json, edges_json, created_at) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s)",
            (str(version_id), str(flowchart_id), 1, nodes_json, edges_json, created_at)
        )
        # Read
        cursor.execute("SELECT version_number FROM flowchart_versions WHERE version_id = %s", (str(version_id),))
        version_data = cursor.fetchone()
        assert version_data is not None and version_data[0] == 1

        # --- Chats Table CRUD ---
        print("Testing Chats table CRUD...")
        chat_id = uuid.uuid4()
        user_id_chat = user_id # Reuse user_id
        created_at = datetime.datetime.now(datetime.timezone.utc)

        # Create
        cursor.execute(
            "INSERT INTO chats (chat_id, user_id, chat_title, created_at) VALUES (%s, %s, %s, %s)",
            (str(chat_id), str(user_id_chat), "Test Chat", created_at)
        )
        # Read
        cursor.execute("SELECT chat_title FROM chats WHERE chat_id = %s", (str(chat_id),))
        chat_data = cursor.fetchone()
        assert chat_data is not None and chat_data[0] == "Test Chat"

        # --- Messages Table CRUD ---
        print("Testing Messages table CRUD...")
        message_id = uuid.uuid4()
        created_at = datetime.datetime.now(datetime.timezone.utc)

        # Create
        cursor.execute(
            "INSERT INTO messages (message_id, chat_id, user_id, message_content, created_at, sender_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (str(message_id), str(chat_id), str(user_id), "Hello", created_at, 'user')
        )
        # Read
        cursor.execute("SELECT message_content FROM messages WHERE message_id = %s", (str(message_id),))
        message_data = cursor.fetchone()
        assert message_data is not None and message_data[0] == "Hello"

        # --- Message Attachments Table CRUD ---
        print("Testing Message Attachments table CRUD...")
        attachment_id = uuid.uuid4()
        created_at = datetime.datetime.now(datetime.timezone.utc)

        # Create
        cursor.execute(
            "INSERT INTO message_attachments (attachment_id, message_id, file_name, created_at) VALUES (%s, %s, %s, %s)",
            (str(attachment_id), str(message_id), "test_file.txt", created_at)
        )
        # Read
        cursor.execute("SELECT file_name FROM message_attachments WHERE attachment_id = %s", (str(attachment_id),))
        attachment_data = cursor.fetchone()
        assert attachment_data is not None and attachment_data[0] == "test_file.txt"

        # --- Nodes Table CRUD ---
        print("Testing Nodes table CRUD...")
        node_id = uuid.uuid4()
        created_at = datetime.datetime.now(datetime.timezone.utc)

        # Create
        cursor.execute(
            "INSERT INTO nodes (node_id, flowchart_id, node_type, created_at) VALUES (%s, %s, %s, %s)",
            (str(node_id), str(flowchart_id), "start", created_at)
        )
        # Read
        cursor.execute("SELECT node_type FROM nodes WHERE node_id = %s", (str(node_id),))
        node_data = cursor.fetchone()
        assert node_data is not None and node_data[0] == "start"

        # --- Edges Table CRUD ---
        print("Testing Edges table CRUD...")
        edge_id = uuid.uuid4()
        source_node_id = node_id # Reuse node_id
        target_node_id = uuid.uuid4() # Create a new target node id, but not inserting into nodes table for simplicity in this test
        created_at = datetime.datetime.now(datetime.timezone.utc)


        # Create
        cursor.execute(
            "INSERT INTO edges (edge_id, flowchart_id, source_node_id, target_node_id, edge_type, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (str(edge_id), str(flowchart_id), str(source_node_id), str(target_node_id), "sequence", created_at)
        )
        # Read
        cursor.execute("SELECT edge_type FROM edges WHERE edge_id = %s", (str(edge_id),))
        edge_data = cursor.fetchone()
        assert edge_data is not None and edge_data[0] == "sequence"


        print("All CRUD tests PASSED!")

        conn.commit()

    except AssertionError:
        conn.rollback()
        print("Assertion failed, transaction rolled back.")
        raise # Re-raise the exception to indicate test failure

    except Exception as e:
        conn.rollback()
        print(f"Exception during CRUD tests: {e}")
        conn.rollback()
        raise # Re-raise the exception to indicate test failure
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    test_crud_operations()