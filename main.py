from flask import Flask, request, render_template, redirect, url_for, session
import os
import subprocess
import sqlite3
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'very_insecure_secret_key'  # Intentionally weak secret key

# Add Content Security Policy headers
@app.after_request
def add_security_headers(response):
    # Strict CSP policy to prevent XSS
    response.headers['Content-Security-Policy'] = (
        "default-src 'none'; "  # Deny everything by default
        "style-src 'self'; "    # Only allow styles from our domain
        "img-src 'self'; "      # Only allow images from our domain
        "script-src 'none'; "   # No scripts allowed
        "frame-src 'none'; "    # No frames allowed
        "object-src 'none'; "   # No plugins allowed
        "base-uri 'none'; "     # Prevent changing the base URL
        "form-action 'self'"    # Forms can only submit to our domain
    )
    return response

# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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

# Login route with rate limiting
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Strict limit to prevent brute force
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

# Command injection vulnerability with rate limiting
@app.route('/ping', methods=['GET'])
@limiter.limit("10 per minute")  # Limit to prevent DoS
def ping():
    ip = request.args.get('ip')
    # Unsafely passing user input to a shell command
    try:
        # Using subprocess.run instead of os.system to capture output
        result = subprocess.run(f"ping -n 1 {ip}", shell=True, capture_output=True, text=True)
        return f"Ping result: {result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"

# SQL injection vulnerability with rate limiting
@app.route('/search')
@limiter.limit("20 per minute")  # Limit to prevent automated SQL injection attempts
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

# XSS vulnerability with rate limiting
@app.route('/comment', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to prevent spam
def comment():
    new_comment = request.form.get('comment', '')
    comments.append(new_comment)  # Storing unescaped comment
    return redirect(url_for('index'))

# Missing function level authorization with rate limiting
@app.route('/admin/delete_user/<user_id>', methods=['POST'])
@limiter.limit("3 per minute")  # Strict limit on admin actions
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
