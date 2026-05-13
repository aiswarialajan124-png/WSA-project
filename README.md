# WSSA-project - Finance Tracker

A personal expense tracking web application built with Flask and SQLite, featuring a dashboard, budget management, and real-time EUR/USD currency conversion.

## Demo

[https://aiswarialajan124.pythonanywhere.com/](https://aiswarialajan124.pythonanywhere.com)

## Login credentials
- Username: `admin`
- Password: `Pass123`

## Features
- **User authentication** : login/logout with session-based user isolation
- **Expense management** : add, edit, and delete expenses with full CRUD via REST API
- **Categories** : 7 preset categories (Food, Transport, Bills, etc.) plus the ability to create custom ones
- **Budget Tracking** : set a monthly budget limit with a live warning banner when spending reaches 80%+
- **Dashboard stats** : total spending, expense count, average spend, and budget remaining
- **Charts** : spending over time (bar chart) and spending by category (doughnut chart) via Chart.js
- **Monthly breakdown** : card grid showing totals and counts per calendar month
- **Currency conversion** : amounts shown in both EUR and USD using hte [opener-api.com](https://open.er-api.com) live exchange rate
- **Filtering & sorting** : filter expenses by description or category, sort by date or amount
- **Responsive design** : works on desktop and mobile

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Database | SQLite |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Charts | Charts.js |
| External API | open.er-api.com (live EUR->USD rate) |
| Hosting | PythonAnywhere |

## Project Structure
```
WSA-project/
├── app.py  # Flask app - all routes and DB logic
├── databases.db
├── templates/
|   └── index.html  # Single-page frontend
└── README.md
```

## REST API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/login` | Authenticate a user |
| GET | `/expenses?user_id=` | Get all expenses for a user |
| POST | `/expenses` | Add a new expense |
| PUT | `/expenses/<id>` | Update an existing expense |
| DELETE | `/expenses/<id>` | Delete an expense |
| GET | `/categories?user_id=` | Get preset + custom categories |
| POST | `/categories` | Add a custom category |
| GET | `/budget?user_id=` | Get the user's monthly budget |
| POST | `/budget` | Set or update the monthly budget |

## Database Schema
**users** : stores login credentials
**expenses** : stores each expense (amount, description, date, category, user)
**categories** : preset and user-created categories
**budget** : one monthly budget limit per user

## Running Locally
1. Clone the repository
2. Install dependancies:
   ```bash
   pip install flask flask-cors
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser

**Note:** The database is created automatically on first run. The hardcoded DB path in `app.py` points to the PythonAnywhere deployment path - update `get_db()` to use relative path (eg. `database.db`) when running locally.

## Testing the API  (Postman / curl)
The API was tested locally using Postman and XAMPP before deployment.

```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Pass123"}'
```

## References
-  Work done during the Web Services and Application module
- [Flask Documentation](https://flask.palletsprojects.com/) — routing, request handling, and templating
- [open.er-api.com](https://open.er-api.com) — live EUR to USD exchange rate API
- [PythonAnywhere Documentation](https://help.pythonanywhere.com/) — deployment and hosting

## Author
Aiswaria Lajan
