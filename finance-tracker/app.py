from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SQLite connection function
def get_db():
    return sqlite3.connect("database.db")

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