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

CREATE_DB_SQL = """
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Flowcharts table
CREATE TABLE IF NOT EXISTS flowcharts (
    flowchart_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_user_id UUID REFERENCES users(user_id),
    flowchart_name VARCHAR(255),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    global_parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Flowchart Versions table
CREATE TABLE IF NOT EXISTS flowchart_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID NOT NULL REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    nodes_json JSONB NOT NULL,
    edges_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chats table
CREATE TABLE IF NOT EXISTS chats (
    chat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    chat_title VARCHAR(255),
    chat_description TEXT,
    session_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    chat_mode VARCHAR(50)
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES chats(chat_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id), -- Nullable for system messages
    message_type VARCHAR(50),
    message_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    message_role VARCHAR(50),
    affects_flowchart BOOLEAN,
    sender_type VARCHAR(50)
);

-- Message Attachments table
CREATE TABLE IF NOT EXISTS message_attachments (
    attachment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_type VARCHAR(255),
    file_size INTEGER,
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Nodes table
CREATE TABLE IF NOT EXISTS nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID NOT NULL REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    node_type VARCHAR(50), -- ENUM in application layer
    api_name VARCHAR(255),
    description TEXT,
    parameters JSONB,
    node_data JSONB,
    position_x INTEGER,
    position_y INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Edges table
CREATE TABLE IF NOT EXISTS edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID NOT NULL REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    source_node_id UUID NOT NULL REFERENCES nodes(node_id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES nodes(node_id) ON DELETE CASCADE,
    edge_type VARCHAR(50), -- ENUM in application layer
    edge_label VARCHAR(255),
    description TEXT,
    edge_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);
"""

def connect_db():
    """Establishes a database connection and creates tables if not exist."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()
        cursor.execute(CREATE_DB_SQL) # Execute SQL to create tables
        conn.commit() # Commit the table creation
        cursor.close()
        return conn
    except psycopg2.Error as e:
        print(f"Database connection or table creation error: {e}")
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

        # Update
        cursor.execute(
            "UPDATE users SET username = %s, email = %s WHERE user_id = %s",
            ("updateduser", "updated@example.com", str(user_id))
        )
        cursor.execute("SELECT username, email FROM users WHERE user_id = %s", (str(user_id),))
        updated_user_data = cursor.fetchone()
        assert updated_user_data is not None and updated_user_data[0] == "updateduser" and updated_user_data[1] == "updated@example.com"

        # Delete
        cursor.execute("DELETE FROM users WHERE user_id = %s", (str(user_id),))
        cursor.execute("SELECT username FROM users WHERE user_id = %s", (str(user_id),))
        deleted_user_data = cursor.fetchone()
        assert deleted_user_data is None

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

        # Update
        cursor.execute(
            "UPDATE flowcharts SET flowchart_name = %s WHERE flowchart_id = %s",
            ("Updated Flowchart Name", str(flowchart_id))
        )
        cursor.execute("SELECT flowchart_name FROM flowcharts WHERE flowchart_id = %s", (str(flowchart_id),))
        updated_flowchart_data = cursor.fetchone()
        assert updated_flowchart_data is not None and updated_flowchart_data[0] == "Updated Flowchart Name"

        # Delete
        cursor.execute("DELETE FROM flowcharts WHERE flowchart_id = %s", (str(flowchart_id),))
        cursor.execute("SELECT flowchart_name FROM flowcharts WHERE flowchart_id = %s", (str(flowchart_id),))
        deleted_flowchart_data = cursor.fetchone()
        assert deleted_flowchart_data is None

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

        # Update
        updated_nodes_json = json.dumps([{"node_id": str(uuid.uuid4()), "node_type": "updated_start"}])
        cursor.execute(
            "UPDATE flowchart_versions SET nodes_json = %s::jsonb WHERE version_id = %s",
            (updated_nodes_json, str(version_id))
        )
        cursor.execute("SELECT nodes_json FROM flowchart_versions WHERE version_id = %s", (str(version_id),))
        updated_version_data = cursor.fetchone()
        assert updated_version_data is not None and json.loads(updated_version_data[0])[0]['node_type'] == "updated_start"

        # Delete
        cursor.execute("DELETE FROM flowchart_versions WHERE version_id = %s", (str(version_id),))
        cursor.execute("SELECT version_number FROM flowchart_versions WHERE version_id = %s", (str(version_id),))
        deleted_version_data = cursor.fetchone()
        assert deleted_version_data is None

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

        # Update
        cursor.execute(
            "UPDATE chats SET chat_title = %s WHERE chat_id = %s",
            ("Updated Chat Title", str(chat_id))
        )
        cursor.execute("SELECT chat_title FROM chats WHERE chat_id = %s", (str(chat_id),))
        updated_chat_data = cursor.fetchone()
        assert updated_chat_data is not None and updated_chat_data[0] == "Updated Chat Title"

        # Delete
        cursor.execute("DELETE FROM chats WHERE chat_id = %s", (str(chat_id),))
        cursor.execute("SELECT chat_title FROM chats WHERE chat_id = %s", (str(chat_id),))
        deleted_chat_data = cursor.fetchone()
        assert deleted_chat_data is None

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

        # Update
        cursor.execute(
            "UPDATE messages SET message_content = %s WHERE message_id = %s",
            ("Updated Message Content", str(message_id))
        )
        cursor.execute("SELECT message_content FROM messages WHERE message_id = %s", (str(message_id),))
        updated_message_data = cursor.fetchone()
        assert updated_message_data is not None and updated_message_data[0] == "Updated Message Content"

        # Delete
        cursor.execute("DELETE FROM messages WHERE message_id = %s", (str(message_id),))
        cursor.execute("SELECT message_content FROM messages WHERE message_id = %s", (str(message_id),))
        deleted_message_data = cursor.fetchone()
        assert deleted_message_data is None

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

        # Update
        cursor.execute(
            "UPDATE message_attachments SET file_name = %s WHERE attachment_id = %s",
            ("updated_file.txt", str(attachment_id))
        )
        cursor.execute("SELECT file_name FROM message_attachments WHERE attachment_id = %s", (str(attachment_id),))
        updated_attachment_data = cursor.fetchone()
        assert updated_attachment_data is not None and updated_attachment_data[0] == "updated_file.txt"

        # Delete
        cursor.execute("DELETE FROM message_attachments WHERE attachment_id = %s", (str(attachment_id),))
        cursor.execute("SELECT file_name FROM message_attachments WHERE attachment_id = %s", (str(attachment_id),))
        deleted_attachment_data = cursor.fetchone()
        assert deleted_attachment_data is None

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

        # Update
        cursor.execute(
            "UPDATE nodes SET node_type = %s WHERE node_id = %s",
            ("updated_start_node", str(node_id))
        )
        cursor.execute("SELECT node_type FROM nodes WHERE node_id = %s", (str(node_id),))
        updated_node_data = cursor.fetchone()
        assert updated_node_data is not None and updated_node_data[0] == "updated_start_node"

        # Delete
        cursor.execute("DELETE FROM nodes WHERE node_id = %s", (str(node_id),))
        cursor.execute("SELECT node_type FROM nodes WHERE node_id = %s", (str(node_id),))
        deleted_node_data = cursor.fetchone()
        assert deleted_node_data is None

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

        # Update
        cursor.execute(
            "UPDATE edges SET edge_type = %s WHERE edge_id = %s",
            ("updated_sequence_edge", str(edge_id))
        )
        cursor.execute("SELECT edge_type FROM edges WHERE edge_id = %s", (str(edge_id),))
        updated_edge_data = cursor.fetchone()
        assert updated_edge_data is not None and updated_edge_data[0] == "updated_sequence_edge"

        # Delete
        cursor.execute("DELETE FROM edges WHERE edge_id = %s", (str(edge_id),))
        cursor.execute("SELECT edge_type FROM edges WHERE edge_id = %s", (str(edge_id),))
        deleted_edge_data = cursor.fetchone()
        assert deleted_edge_data is None


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