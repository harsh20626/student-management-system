import sqlite3
import hashlib
import os
from datetime import datetime

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    # Read schema file
    with open('StudentTaskManagementSystem/database/schema.sql', 'r') as f:  # Updated path
        schema = f.read()
    
    # Connect to database and create tables
    conn = sqlite3.connect('student_productivity.db')
    try:
        conn.executescript(schema)
        print("Database initialized successfully!")
        
        # Create test user if it doesn't exist
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'test'")
        if not cursor.fetchone():
            test_user = {
                'username': 'test',
                'password': hash_password('test123'),
                'email': 'test@example.com'
            }
            cursor.execute("""
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            """, (test_user['username'], test_user['password'], test_user['email']))
            print("Test user created successfully!")
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def reset_db():
    """Reset the database by removing and reinitializing it."""
    try:
        os.remove('student_productivity.db')
        print("Existing database removed.")
    except FileNotFoundError:
        pass
    
    init_db()

if __name__ == "__main__":
    while True:
        choice = input("Choose action:\n1. Initialize DB\n2. Reset DB\n3. Exit\nChoice: ")
        if choice == '1':
            init_db()
        elif choice == '2':
            confirmation = input("Are you sure you want to reset the database? (y/n): ")
            if confirmation.lower() == 'y':
                reset_db()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")
