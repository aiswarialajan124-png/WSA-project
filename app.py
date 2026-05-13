from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection
def get_db():
    conn = sqlite3.connect("database.db")
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

# Expenses

# GET /expenses?user_id=1
@app.route('/expenses', methods=['GET'])
def get_expenses():
    user_id = request.args.get('user_id')
    db = get_db()
    cursor = db.cursor()

    if user_id:
        cursor.execute("""
            SELECT e.id, e.amount, e.description, e.date, e.useR_id, e.cateory_id, c.name
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ?
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT e.id,e.amount, e.description, e.date, e.user_id, e.category_id, c.name
            FROM  expenses e
            LEFT JOIN categories c ON e.category_id = c.id
        """)

    rows = cursor.fetchall()
    expenses = []
    for row in rows:
        expenses.append({
            "id": row[0],
            "amount": row[1],
            "description": row[2],
            "date": row[3],
            "user_id": row[4],
            "category_id": row[5],
            "category_name": row[6]
        })
    db.close()
    return jsonify(expenses)

# POST /expenses
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
        data.get('category_id', 1),
        data['user_id'],
        data['date']
    ))

    db.commit()
    db.close()
    return jsonify({"message": "Expenses added successfully"})

# PUT /expenses/<id>
@app.route('/expenses/<int:id>', methods=['PUT'])
def edit_expenses(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE expenses
        SET amount = ?, description = ?, category_id = ?, date = ?
        WHERE id = ?
    """, (
        data['amount'],
        data['description'],
        data.get('category_id', 1),
        data['date'],
        id
    ))

    db.commit()
    db.close()
    return jsonify({"message": "Expenses updated successfully"})

# DELETE /expenses/<id>
@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expenses(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"message": "Deleted"})

# Categories

# GET /categories?user_id=1
@app.route('/categories', methods=['GET'])
def get_categories():
    user_id = request.args.get('user_id')
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, name, user_id FROM categories
        WHERE user_id IS NULL OR user_id = ?
        ORDER BY user_id IS NULL DESC, name ASC
    """, (user_id,))

    rows = cursor.fetchall()
    categories = []
    for row in rows:
        categories.append({
            "id": row[0],
            "name": row[1],
            "user_id": row[2]
        })
    db.close()
    return jsonify(categories)

# POST /categories
@app.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id FROM categories
        WHERE name = ? AND (user_id = ? OR user_id IS NULL)
    """, (data['name'], data['user_id']))

    if cursor.fetchone():
        db.close()
        return jsonify({"message": "Category already exists"}), 409

    cursor.execute("""
        INSERT INTO categories (name, user_id) VALUES (?, ?)
    """, (data['name'], data['user_id']))

    new_id = cursor.lastrowid
    db.commit()
    db.close()
    return jsonify({"message": "Category added", "id": new_id})

# Budget

# GET /budget?user_id=1
@app.route('/budget', methods=['GET'])
def get_budget():
    user_id = request.args.get('user_id')
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT amount FROM budgets WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    db.close()

    if row:
        return jsonify({"amount": row["amount"]})
    else:
        return jsonify({"amount": None})

# POST /budget
@app.route('/budget', methods=['POST'])
def set_budget():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO budgets (user_id, amount)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET amount = excluded.amount
    """, (data['user_id'], data['amount']))

    db.commit()
    db.close()
    return jsonify({"message": "Budget saved"})

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (data['username'], data['password'])
    )

    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": user[0]
        })
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Serve Frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)