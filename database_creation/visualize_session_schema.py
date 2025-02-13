import psycopg2
import graphviz

# Database connection details for "ocotolobus"
DB_HOST = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
DB_NAME = "ocotolobus"  # Changed DB_NAME to "ocotolobus"
DB_USER = "ocotolobus"
DB_PASSWORD = "WcM1hCwTVBfm6XnvXm29"
DB_PORT = 5432

CREATE_DB_SQL_FOR_VISUALIZATION = """
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

-- Sessions table (replaces flowchart_versions)
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID REFERENCES flowcharts(flowchart_id),
    chat_id UUID REFERENCES chats(chat_id),
    session_status VARCHAR(50),
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

-- Messages table (userid column removed)
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

def visualize_db_schema_with_session():
    """Connects to the database, retrieves schema, and visualizes it using Graphviz."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()

        # Use the CREATE_DB_SQL_FOR_VISUALIZATION schema for visualization
        cursor.execute(f"""
            DROP TABLE IF EXISTS edges CASCADE;
            DROP TABLE IF EXISTS nodes CASCADE;
            DROP TABLE IF EXISTS message_attachments CASCADE;
            DROP TABLE IF EXISTS messages CASCADE;
            DROP TABLE IF EXISTS chats CASCADE;
            DROP TABLE IF EXISTS sessions CASCADE;
            DROP TABLE IF EXISTS flowchart_versions CASCADE; 
            DROP TABLE IF EXISTS flowcharts CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            {CREATE_DB_SQL_FOR_VISUALIZATION}
        """)
        conn.commit()

        # SQL query to fetch table and column information (PostgreSQL specific)
        cursor.execute("""
            SELECT 
                table_name, 
                column_name, 
                data_type, 
                ordinal_position,
                column_name || ' ' || data_type AS column_label
            FROM 
                information_schema.columns
            WHERE 
                table_schema = 'public'
            ORDER BY 
                table_name, 
                ordinal_position;
        """)
        columns_data = cursor.fetchall()

        # SQL query to fetch foreign key relationships (PostgreSQL specific)
        cursor.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM 
                information_schema.table_constraints AS tc
            JOIN 
                information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            JOIN 
                information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = ccu.table_schema
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
        """)
        fk_relationships = cursor.fetchall()

        dot = graphviz.Digraph('database_schema_with_session', comment='Database Schema Visualization with Session Table', graph_attr={'rankdir': 'LR', 'fontname': 'Arial Unicode MS'})

        tables = {} # Dictionary to hold table nodes

        # Create table nodes
        for table_name, column_name, data_type, ordinal_position, column_label in columns_data:
            if table_name not in tables:
                tables[table_name] = []
            tables[table_name].append(column_label)

        for table_name, columns in tables.items():
            table_label = f"<<TABLE><TR><TD COLSPAN='2' ALIGN='CENTER'>{table_name}</TD></TR>"
            for column in columns:
                table_label += f"<TR><TD ALIGN='LEFT'>-</TD><TD ALIGN='LEFT'>{column}</TD></TR>"
            table_label += "</TABLE>>"
            dot.node(table_name, table_label, shape='plaintext')

        # Create edges for foreign key relationships
        for table_name, column_name, foreign_table_name, foreign_column_name in fk_relationships:
            dot.edge(table_name, foreign_table_name, label=f"{column_name} -> {foreign_column_name}")

        dot.render('ocotolobus_session_schema_visualization', format='png', view=False)
        print("Database schema visualization with session table saved to ocotolobus_session_schema_visualization.png")

    except psycopg2.Error as e:
        print(f"Database connection or schema visualization error: {e}")
    except Exception as e:
        print(f"Error generating database schema visualization: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    visualize_db_schema_with_session()