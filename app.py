from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database configuration
DB_PATH = 'users.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with users table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample users if table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        sample_users = ['toms', 'alice', 'bob', 'charlie']
        for username in sample_users:
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

@app.route('/api/verify', methods=['GET', 'POST'])
def verify_user():
    """Verify if user exists in database"""
    username = request.headers.get('X-Username') or request.headers.get('Username')
    
    if not username:
        return jsonify({
            'error': 'Username header missing',
            'message': 'Please provide username in X-Username or Username header'
        }), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'success': True,
            'message': f'User {username} exists',
            'username': username
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': f'User {username} not found',
            'username': username
        }), 404

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, created_at FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()
    
    users_list = [{'id': user['id'], 'username': user['username'], 'created_at': user['created_at']} for user in users]
    
    return jsonify({
        'success': True,
        'count': len(users_list),
        'users': users_list
    }), 200

@app.route('/api/users', methods=['POST'])
def add_user():
    """Add a new user to the database"""
    data = request.get_json()
    
    if not data or 'username' not in data:
        return jsonify({
            'error': 'Username is required',
            'message': 'Please provide username in request body'
        }), 400
    
    username = data['username']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'User {username} added successfully',
            'username': username
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({
            'error': 'User already exists',
            'message': f'User {username} already exists in database'
        }), 409

@app.route('/api/users/<username>', methods=['DELETE'])
def delete_user(username):
    """Delete a user from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({
            'success': False,
            'message': f'User {username} not found'
        }), 404
    
    # Delete user
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'User {username} deleted successfully'
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with embedded HTML"""
    html_content = '''<!DOCTYPE html> 
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 30px; }
        .section { margin-bottom: 40px; }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-danger {
            background: #e74c3c;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
        }
        .btn-danger:hover {
            background: #c0392b;
            transform: translateY(-1px);
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .users-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .users-table th, .users-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .users-table th {
            background: #f8f9fa;
            color: #667eea;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        .users-table tr:hover { background: #f8f9fa; }
        .user-count {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-size: 1.2em;
        }
        .no-users {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👥 User Management System</h1>
            <p>Manage users with ease</p>
        </div>
        <div class="content">
            <!-- Add User Section -->
            <div class="section">
                <h2>➕ Add New User</h2>
                <div id="addMessage" class="message"></div>
                <form id="addUserForm">
                    <div class="form-group">
                        <label for="newUsername">Username:</label>
                        <input type="text" id="newUsername" name="username" placeholder="Enter username" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Add User</button>
                </form>
            </div>

            <!-- Users List Section -->
            <div class="section">
                <h2>📋 All Users</h2>
                <div id="userCount" class="user-count">Loading...</div>
                <div id="usersContainer">
                    <div class="loading">Loading users...</div>
                </div>
            </div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() { loadUsers(); });
        
        document.getElementById('addUserForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('newUsername').value.trim();
            const messageDiv = document.getElementById('addMessage');
            try {
                const response = await fetch('/api/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: username })
                });
                const data = await response.json();
                if (response.ok) {
                    showMessage(messageDiv, data.message, 'success');
                    document.getElementById('addUserForm').reset();
                    loadUsers();
                } else {
                    showMessage(messageDiv, data.message || data.error, 'error');
                }
            } catch (error) {
                showMessage(messageDiv, 'Error adding user: ' + error.message, 'error');
            }
        });
        
        async function loadUsers() {
            const container = document.getElementById('usersContainer');
            const countDiv = document.getElementById('userCount');
            try {
                const response = await fetch('/api/users');
                const data = await response.json();
                if (response.ok && data.users) {
                    countDiv.textContent = `Total Users: ${data.count}`;
                    if (data.users.length === 0) {
                        container.innerHTML = '<div class="no-users">No users found. Add some users to get started!</div>';
                    } else {
                        let tableHTML = '<table class="users-table"><thead><tr><th>ID</th><th>Username</th><th>Created At</th><th>Actions</th></tr></thead><tbody>';
                        data.users.forEach(user => {
                            tableHTML += `<tr><td>${user.id}</td><td>${user.username}</td><td>${new Date(user.created_at).toLocaleString()}</td><td><button class="btn btn-danger" onclick="deleteUser('${user.username}')">Delete</button></td></tr>`;
                        });
                        tableHTML += '</tbody></table>';
                        container.innerHTML = tableHTML;
                    }
                } else {
                    container.innerHTML = '<div class="no-users">Error loading users</div>';
                }
            } catch (error) {
                container.innerHTML = '<div class="no-users">Error loading users: ' + error.message + '</div>';
            }
        }
        
        async function deleteUser(username) {
            if (!confirm(`Are you sure you want to delete user "${username}"?`)) { return; }
            try {
                const response = await fetch(`/api/users/${username}`, { method: 'DELETE' });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    loadUsers();
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                alert('Error deleting user: ' + error.message);
            }
        }
        
        function showMessage(element, message, type) {
            element.textContent = message;
            element.className = `message ${type}`;
            element.style.display = 'block';
            setTimeout(() => { element.style.display = 'none'; }, 5000);
        }
    </script>
</body>
</html>'''
    return html_content

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'User Management API',
        'endpoints': {
            '/': 'Visual database viewer',
            '/api/verify': 'Verify user exists (requires X-Username header)',
            '/api/users': 'GET: List all users, POST: Add new user',
            '/api/users/<username>': 'DELETE: Delete a user',
            '/api/info': 'This API information'
        }
    }), 200

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run the Flask app on PORT 5009 to avoid conflict with AirPlay
   
    print("Local URL: http://127.0.0.1:5009")
    print("Network URL: http://0.0.0.0:5009")
   
    app.run(debug=True, host='0.0.0.0', port=5009)

