#!/usr/bin/env python
"""
Script to create database schema from SQL file.
This script reads the SQL file and executes it using Django's database connection.
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_celulares.settings')
django.setup()

def execute_sql_file(sql_file_path):
    """Execute SQL commands from a file."""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split SQL statements (basic splitting by semicolon)
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        with connection.cursor() as cursor:
            for statement in sql_statements:
                if statement:
                    print(f"Executing: {statement[:50]}...")
                    cursor.execute(statement)
        
        print("Database schema created successfully!")
        
    except Exception as e:
        print(f"Error executing SQL file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    sql_file = os.path.join(os.path.dirname(__file__), 'create_database_schema.sql')
    
    if not os.path.exists(sql_file):
        print(f"SQL file not found: {sql_file}")
        sys.exit(1)
    
    print(f"Executing SQL file: {sql_file}")
    success = execute_sql_file(sql_file)
    
    if not success:
        sys.exit(1)
