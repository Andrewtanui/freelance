import sqlite3
from datetime import datetime

def update_users_table():
    """Add created_at column to users table and set default values"""
    try:
        # Connect to the database
        conn = sqlite3.connect('./instance/database.db')
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT
            # So we need to use a workaround
            
            # 1. Create a new table with the desired schema
            cursor.execute('''
                CREATE TABLE users_new (
                    id VARCHAR(36) PRIMARY KEY,
                    firstname VARCHAR(64) NOT NULL,
                    lastname VARCHAR(64) NOT NULL,
                    password VARCHAR(128),
                    email VARCHAR(120) UNIQUE,
                    role VARCHAR(10) NOT NULL,
                    phonenumber VARCHAR(15),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Copy data from the old table to the new one
            cursor.execute('''
                INSERT INTO users_new (id, firstname, lastname, password, email, role, phonenumber, created_at)
                SELECT id, firstname, lastname, password, email, role, phonenumber, CURRENT_TIMESTAMP
                FROM users
            ''')
            
            # 3. Drop the old table
            cursor.execute('DROP TABLE users')
            
            # 4. Rename the new table to the original name
            cursor.execute('ALTER TABLE users_new RENAME TO users')
            
            print("Successfully added created_at column to users table")
        else:
            print("created_at column already exists in users table")
        
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error updating users table: {e}")
        return False

if __name__ == "__main__":
    update_users_table()
