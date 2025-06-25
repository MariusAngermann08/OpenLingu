import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/languages.db')
DB_PATH = os.path.abspath(DB_PATH)

def print_table_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n--- Table Schema for 'lections' ---")
    cursor.execute("PRAGMA table_info(lections);")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    conn.close()

def print_json_extract():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n--- json_extract(content, '$.id') for all lections ---")
    try:
        cursor.execute("SELECT id, json_extract(content, '$.id') FROM lections;")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Lection DB id: {row[0]}, content.id: {row[1]}")
    except Exception as e:
        print(f"Error running json_extract: {e}")
    conn.close()

if __name__ == "__main__":
    print_table_schema()
    print_json_extract()
