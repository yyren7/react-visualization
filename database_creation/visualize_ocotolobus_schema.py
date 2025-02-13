import psycopg2
import graphviz

# Database connection details for "ocotolobus"
DB_HOST = "otocolobus.c3imo6ogk8ee.ap-southeast-2.rds.amazonaws.com"
DB_NAME = "ocotolobus"  # Changed DB_NAME to "ocotolobus"
DB_USER = "otocolobus"
DB_PASSWORD = "WcM1hCwTVBfm6XnvXm29"
DB_PORT = 5432

def visualize_db_schema():
    """Connects to the database, retrieves schema, and visualizes it using Graphviz."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        cursor = conn.cursor()

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

        dot = graphviz.Digraph('database_schema', comment='Database Schema Visualization', graph_attr={'rankdir': 'LR', 'fontname': 'Arial Unicode MS'})

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

        dot.render('ocotolobus_schema_visualization', format='png', view=False)
        print("Database schema visualization saved to ocotolobus_schema_visualization.png")

    except psycopg2.Error as e:
        print(f"Database connection or schema visualization error: {e}")
    except Exception as e:
        print(f"Error generating database schema visualization: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    visualize_db_schema()