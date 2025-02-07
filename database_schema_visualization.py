import psycopg2
import graphviz

try:
    conn = psycopg2.connect(user='otocolobus', password='am', dbname='otocolobus')
    cursor = conn.cursor()

    # 获取所有表
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [table[0] for table in cursor.fetchall()]

    # 获取所有列
    columns = {}
    for table in tables:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
        columns[table] = cursor.fetchall()

    # 获取所有外键关系
    cursor.execute("""
        SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
    """)
    relations = cursor.fetchall()

    dot = graphviz.Digraph('database_schema', comment='Database Schema Visualization', graph_attr={'rankdir': 'TB', 'splines': 'ortho'})

    for table in tables:
        label = f"<<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\">\n  <TR><TD BGCOLOR=\"lightblue\"><b>{table}</b></TD></TR>"
        for column_name, data_type in columns[table]:
            label += f"\n  <TR><TD ALIGN=\"LEFT\">{column_name} : {data_type}</TD></TR>"
        label += "\n</TABLE>>"
        dot.node(table, label=label)

    for table_name, column_name, foreign_table_name, foreign_column_name in relations:
        dot.edge(table_name, foreign_table_name, label=f"{column_name} -> {foreign_column_name}")

    dot.render('database_schema', format='png', view=False)
    print("Database schema visualization saved to database_schema.png")

    conn.close()

except Exception as e:
    print(f"Error generating database schema visualization: {e}")