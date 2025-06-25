from sqlalchemy import create_engine, text, inspect
import os
import json

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'languages.db')

# Create SQLAlchemy engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Create an inspector
inspector = inspect(engine)

# List all tables
print("Tables in the database:")
tables = inspector.get_table_names()
for table in tables:
    print(f"\nTable: {table}")
    
    # Get columns
    columns = inspector.get_columns(table)
    print("\nColumns:")
    for column in columns:
        print(f"- {column['name']}: {column['type']} (Primary Key: {column.get('primary_key', False)})")
    
    # Get sample data
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5;"))
            rows = result.fetchall()
            
            print(f"\nSample data (first 5 rows):")
            for row in rows:
                print(row)
                
                # If this is the lections table and has content, show its type and a preview
                if table == 'lections' and 'content' in [c['name'] for c in columns]:
                    content = row.content if hasattr(row, 'content') else dict(row).get('content')
                    print(f"  Content type: {type(content)}")
                    if content:
                        try:
                            if isinstance(content, str):
                                parsed = json.loads(content)
                                print(f"  Content (parsed): {json.dumps(parsed, indent=2)[:200]}...")
                            else:
                                print(f"  Content: {str(content)[:200]}...")
                        except json.JSONDecodeError:
                            print(f"  Content (raw): {str(content)[:200]}...")
                    print("-" * 50)
                    
    except Exception as e:
        print(f"Error reading table {table}: {e}")
    
    print("\n" + "="*80 + "\n")
