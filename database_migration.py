import psycopg2

try:
    conn = psycopg2.connect(user='otocolobus', password='am', dbname='otocolobus')
    cursor = conn.cursor()

    # 检查外键约束是否存在
    cursor.execute("SELECT constraint_name FROM information_schema.table_constraints WHERE table_name = 'messages' AND constraint_type = 'FOREIGN KEY' AND constraint_name = 'messages_chat_id_fkey'")
    constraint_exists = cursor.fetchone()

    if not constraint_exists:
        # 添加外键约束
        cursor.execute("ALTER TABLE messages ADD CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES chats(chat_id)")
        conn.commit()
        print("Added messages_chat_id_fkey constraint to messages table")
    else:
        print("messages_chat_id_fkey constraint already exists on messages table")

    conn.commit()
    conn.close()

except Exception as e:
    print(f"Connection or query error: {e}")
