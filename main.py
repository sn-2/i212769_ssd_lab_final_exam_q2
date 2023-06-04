from flask import Flask, request
import os
import subprocess
import sqlite3

app = Flask(__name__)

# Insecure direct object reference (IDOR) vulnerability
@app.route('/user/<username>')
def user_profile(username):
    # No checks for whether this user belongs to the currently authenticated user
    return "Profile of " + username

# Command injection vulnerability
@app.route('/ping')
def ping():
    ip = request.args.get('ip')
    # Unsafely passing user input to a shell command
    response = os.system("ping -c 1 " + ip)
    return "Pinged: " + ip

# SQL injection vulnerability
@app.route('/search')
def search():
    query = request.args.get('q')
    # Unsafely incorporating user input into a SQL query
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE name LIKE '%" + query + "%'")
    return str(cursor.fetchall())

# Cross-Site Scripting (XSS) vulnerability
@app.route('/comment', methods=['POST'])
def comment():
    comment = request.form.get('comment')
    # Output includes unescaped user input
    return 'You said: ' + comment

# Missing function level authorization
@app.route('/admin/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # No checks whether the current user has the right to delete users
    print("Deleted {}".format(user_id))
    pass

if __name__ == '__main__':
    app.run(debug=True)
