import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/languages.db')
DB_PATH = os.path.abspath(DB_PATH)


def migrate_lections_content_to_json():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Read all lections and parse their content
    print("Reading existing lections...")
    cursor.execute("SELECT id, title, description, language, difficulty, created_at, created_by, content FROM lections")
    lections = []
    for row in cursor.fetchall():
        id_, title, description, language, difficulty, created_at, created_by, content = row
        try:
            content_dict = json.loads(content) if content else {}
        except Exception as e:
            print(f"Warning: Could not decode content for lection '{title}': {e}. Using empty dict.")
            content_dict = {}
        lections.append((id_, title, description, language, difficulty, created_at, created_by, content_dict))
    print(f"Found {len(lections)} lections.")

    # 2. Rename old table
    print("Renaming old table...")
    cursor.execute("ALTER TABLE lections RENAME TO lections_old;")

    # 3. Create new table with JSON type for content
    print("Creating new lections table with JSON content column...")
    cursor.execute('''
        CREATE TABLE lections (
            id VARCHAR NOT NULL PRIMARY KEY,
            title VARCHAR,
            description VARCHAR,
            language VARCHAR,
            difficulty VARCHAR,
            created_at DATETIME,
            created_by VARCHAR,
            content JSON
        );
    ''')

    # 4. Insert data back
    print("Re-inserting lections...")
    for lec in lections:
        cursor.execute('''
            INSERT INTO lections (id, title, description, language, difficulty, created_at, created_by, content)
            VALUES (?, ?, ?, ?, ?, ?, ?, json(?))
        ''', (
            lec[0], lec[1], lec[2], lec[3], lec[4], lec[5], lec[6], json.dumps(lec[7], ensure_ascii=False)
        ))
    print("All lections re-inserted.")

    # 5. Drop old table
    print("Dropping old table...")
    cursor.execute("DROP TABLE lections_old;")
    conn.commit()
    conn.close()
    print("Migration complete! Your lections table now uses a JSON column for content.")

if __name__ == "__main__":
    migrate_lections_content_to_json()
