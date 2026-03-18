from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="", # default XAMPP
    database="finance_app"
)

@app.route('/expenses', methods=['GET'])
def get_expenses():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses")
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    cursor = db.cursor()

    sql = """INSERT INTO expenses
              (amount, description, category_id, user_id, date)
              VALUES (%s, %s, %s, %s, %s)"""

    values = (
        data['amount'],
        data['description'],
        data['category_id'],
        data['user_id'],
        data['date']
    )

    cursor.execute(sql, values)
    db.commit()

    return jsonify({"message": "Expenses added successfully"})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)