
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import stripe
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Stripe configuration
stripe.api_key = 'sk_test_51RDloGP3dWxXKAsQujJ4rEdJ6njcrfSsQsAOr105BZO8X4SLSRbveGo8eUPnv9nXNZm19RQ2gLM23jr7ZlKFBxUJ00ldqIwxeQ'  # Replace with actual secret key
STRIPE_PUBLIC_KEY = 'pk_test_51RDloGP3dWxXKAsQU0GXapHiR7UiscDdGLsn8UQIIke6tHhaNWtWuAvhTOk5jkFfy8Ko6fqtiuK14CJVd1JtzZ5R00UIXHHxh4'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    renew_date = db.Column(db.Date, nullable=False)
    platform = db.Column(db.String(100))
    category = db.Column(db.String(100))

@app.route('/admin')
def admin_dashboard():
    users = User.query.all()
    all_subs = Subscription.query.all()

    # Get total counts and amount
    total_users = len(users)
    total_subs = len(all_subs)
    total_amount = sum(sub.amount for sub in all_subs)

    # Prepare user-wise subscription count and total
    user_data = []
    for user in users:
        user_subs = Subscription.query.filter_by(user_id=user.id).all()
        sub_count = len(user_subs)
        sub_total = sum(s.amount for s in user_subs)
        user_data.append({
            'username': user.username,
            'count': sub_count,
            'total': sub_total
        })

    return render_template(
        'admin.html',
        users=users,
        subscriptions=all_subs,
        total_users=total_users,
        total_subs=total_subs,
        total_amount=total_amount,
        user_data=user_data
    )


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    subs = Subscription.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', subscriptions=subs, stripe_key=STRIPE_PUBLIC_KEY)

@app.route('/add', methods=['GET', 'POST'])
def add_subscription():
    if request.method == 'POST':
        new_sub = Subscription(
            user_id=session['user_id'],
            name=request.form['name'],
            amount=float(request.form['amount']),
            renew_date=datetime.strptime(request.form['renew_date'], '%Y-%m-%d'),
            platform=request.form['platform'],
            category=request.form['category']
        )
        db.session.add(new_sub)
        db.session.commit()
        flash("Subscription added!", "success")
        return redirect(url_for('dashboard'))
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_subscription(id):
    sub = Subscription.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    flash("Subscription deleted.", "info")
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_subscription(id):
    sub = Subscription.query.get_or_404(id)
    if request.method == 'POST':
        sub.name = request.form['name']
        sub.amount = float(request.form['amount'])
        sub.renew_date = datetime.strptime(request.form['renew_date'], '%Y-%m-%d')
        sub.platform = request.form['platform']
        sub.category = request.form['category']
        db.session.commit()
        flash("Subscription updated.", "success")
        return redirect(url_for('dashboard'))
    return render_template('edit.html', sub=sub)

@app.route('/checkout/<int:sub_id>')
def checkout(sub_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    sub = Subscription.query.get_or_404(sub_id)
    session_stripe = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': int(sub.amount * 100),
                'product_data': {
                    'name': sub.name,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('dashboard', _external=True),
        cancel_url=url_for('dashboard', _external=True),
    )
    return redirect(session_stripe.url)

if __name__ == '__main__':
    if not os.path.exists('subscriptions.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
