import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_database():
    """Create database with exact PDF schema + your current fields"""
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect('clauseease.db')
    cursor = conn.cursor()
    
    print("🗄️ Creating database tables...")
    
    # USERS TABLE (PDF schema + your current fields)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # DOCUMENTS TABLE (from PDF)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            document_title VARCHAR(255),
            original_text TEXT,
            simplified_text_basic TEXT,
            simplified_text_intermediate TEXT,
            simplified_text_advanced TEXT,
            original_readability_score FLOAT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # GLOSSARY TABLE (from PDF)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS glossary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term VARCHAR(100) UNIQUE NOT NULL,
            simplified_explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # USER SESSIONS TABLE (for login tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    print("✅ Database tables created successfully!")
    
    # Create admin user
    create_admin_user(cursor)
    
    # Add sample glossary terms
    add_sample_glossary(cursor)
    
    conn.commit()
    conn.close()
    print("🎯 Database setup complete!")

def create_admin_user(cursor):
    """Create admin user for dashboard access"""
    print("👑 Creating admin user...")
    
    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        print("ℹ️ Admin user already exists")
        return
    
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    ''', ('admin', 'admin@clauseease.com', admin_password))
    
    print("✅ Admin user created: admin / admin123")

def add_sample_glossary(cursor):
    """Add sample legal terms for glossary"""
    print("📚 Adding sample glossary terms...")
    
    sample_terms = [
        ('Liability', 'Legal responsibility for damages or losses'),
        ('Indemnify', 'To protect someone from legal responsibility for damages'),
        ('Breach', 'Breaking or violating the terms of an agreement'),
        ('Jurisdiction', 'The authority of a court to hear and decide a case'),
        ('Force Majeure', 'Unforeseeable circumstances that prevent a party from fulfilling a contract')
    ]
    
    for term, explanation in sample_terms:
        cursor.execute('''
            INSERT OR IGNORE INTO glossary (term, simplified_explanation, created_by)
            VALUES (?, ?, 1)
        ''', (term, explanation))
    
    print("✅ Sample glossary added!")

if __name__ == "__main__":
    create_database()
