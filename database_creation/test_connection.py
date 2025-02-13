import psycopg2

# Database connection details
DB_HOST = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
DB_NAME = "ocotolobus"  # Changed DB_NAME to "ocotolobus"
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

def test_db_connection():
    """Tests database connection, creates database if not exists, and applies v16 schema."""
    conn = None
    try:
        # Connect to postgres database to create a new database
        conn_admin = psycopg2.connect(host=DB_HOST, database="postgres", user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        conn_admin.autocommit = True  # Set autocommit to True for CREATE DATABASE
        cursor_admin = conn_admin.cursor()

        try:
            # Try to create the database, ignore if it already exists
            cursor_admin.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully!")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{DB_NAME}' already exists, proceeding with schema creation.")
        finally:
            conn_admin.close()

        # Now connect to the newly created or existing database "ocotolobus"
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()


        # Apply v16 schema
        cursor.execute(CREATE_DB_SQL)
        conn.commit()
        print(f"v16 schema applied to database '{DB_NAME}' successfully!")
        print(f"Successfully connected to database '{DB_NAME}'!")
        return True

    except psycopg2.Error as e:
        print(f"Database operation failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_db_connection()