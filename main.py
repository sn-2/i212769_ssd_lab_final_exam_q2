from flask import Flask, request, render_template, redirect, url_for, session
import os
import subprocess
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'very_insecure_secret_key'  # Intentionally weak secret key

# In-memory storage for comments (insecure)
comments = []

# Database initialization
def init_db():
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    # Create users table without proper password hashing
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, is_admin BOOLEAN)''')
    
    # Add some test users with plaintext passwords
    c.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
              ("admin", "admin123", True))
    c.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
              ("user", "password123", False))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Insecure login without rate limiting
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = c.execute(query).fetchone()
    conn.close()
    
    if user:
        session['logged_in'] = True
        session['username'] = username
        session['is_admin'] = user[3]
        return redirect(url_for('index'))
    return 'Invalid credentials', 401

# Insecure direct object reference (IDOR) vulnerability
@app.route('/user/<username>')
def user_profile(username):
    # No checks for whether this user belongs to the currently authenticated user
    return f"Profile of {username}"

# Command injection vulnerability
@app.route('/ping', methods=['GET'])
def ping():
    ip = request.args.get('ip')
    # Unsafely passing user input to a shell command
    try:
        # Using subprocess.run instead of os.system to capture output
        result = subprocess.run(f"ping -n 1 {ip}", shell=True, capture_output=True, text=True)
        return f"Ping result: {result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"

# SQL injection vulnerability
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Unsafely incorporating user input into a SQL query
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM users WHERE username LIKE '%{query}%'")
        results = cursor.fetchall()
        return str(results)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        connection.close()

# XSS vulnerability
@app.route('/comment', methods=['POST'])
def comment():
    new_comment = request.form.get('comment', '')
    comments.append(new_comment)  # Storing unescaped comment
    return redirect(url_for('index'))

# Missing function level authorization
@app.route('/admin/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    # No checks whether the current user has the right to delete users
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM users WHERE id = {user_id}")  # SQL injection vulnerability
    conn.commit()
    conn.close()
    return f"User {user_id} deleted"

# Main route
@app.route('/')
def index():
    return render_template('base.html', comments=comments)

if __name__ == '__main__':
    # Running with debug=True exposes debug information
    app.run(debug=True, host='0.0.0.0')  # Intentionally binding to all interfaces
