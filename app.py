from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection 
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row # Allows to access columns by name instead of index
    return conn

# Database setup
def init_db():
    db = get_db()
    cursor = db.cursor()

    # User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # Budget Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Insert preset categories if they do not exist yet
    presets = ['Food', 'Transport', 'Bills', 'Entertainment', 'Health', 'Shopping', 'Other']
    for name in presets:
        cursor.execute("""
            INSERT INTO categories (name, user_id)
            SELECT ?, NULL WHERE NOT EXISTS (
                SELECT 1 FROM categories WHERE name = ? AND user_id IS NULL
            )
        """, (name, name))

    db.commit()
    db.close()

init_db()

@app.route('/expenses', methods=['GET'])
def get_expenses():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    expenses = []
    for row in rows:
        expenses.append({
            "id": row[0],
            "amount": row[1],
            "description": row[2],
            "date": row[3],
            "user_id": row[4],
            "category_id": row[5]
        })
    return jsonify(expenses)

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
                   INSERT INTO expenses (amount, description, category_id, user_id, date)
                   VALUES (?, ?, ?, ?, ?)
    """, (
        data['amount'],
        data['description'],
        data['category_id'],
        data['user_id'],
        data['date']
    ))

    db.commit()

    return jsonify({"message": "Expenses added successfully"})

@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expenses(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    db.commit()

    return jsonify({"message": "Deleted"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data['username'], data['password'])
    )

    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": user[0]
        })
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)