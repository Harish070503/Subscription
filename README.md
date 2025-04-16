# 🧾 Subscription Management System

A **Flask-based web application** that allows users to manage their paid subscriptions, track renewal dates, and make payments using **Stripe Checkout**. It includes user authentication, an admin dashboard, and full CRUD functionality for subscriptions.

---

## 🚀 Features

- 🔐 User registration & login with password hashing
- 📋 Add, edit, and delete subscriptions
- 📅 Track subscription renewal dates
- 💳 Stripe integration for payments
- 📊 Admin dashboard with:
  - Total users
  - Total subscriptions
  - Total revenue
  - User-wise subscription stats
- ⚡ Flash messages for user feedback

---

## 🛠 Tech Stack

- **Backend:** Flask, SQLAlchemy
- **Database:** SQLite
- **Authentication:** Flask Sessions + Werkzeug
- **Payments:** Stripe API
- **Frontend:** HTML, CSS (via Jinja templates)
- **Deployment-ready:** Python built-in server

---

## 🔧 Installation

Follow these steps to run the project locally:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/subscription-management.git
cd subscription-management

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your Stripe API keys
# Replace 'sk_test_...' and 'pk_test_...' inside app.py with your actual keys

# 5. Run the application
python app.py

# 6. Visit the app in your browser
http://127.0.0.1:5000

