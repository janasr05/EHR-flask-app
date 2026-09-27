from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import io, csv, os
from datetime import datetime

app = Flask(__name__)

# 🔐 Secret Key
app.secret_key = "your_secret_key"

# 🗄 Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- DATABASE ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200))

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return redirect(url_for('login'))

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash("Email already registered", "warning")
            return redirect(url_for('login'))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            flash("Login successful", "success")
            return redirect(url_for('index'))

        flash("Invalid credentials", "danger")

    return render_template('login.html')

# INDEX (DASHBOARD)
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# RESULT
@app.route('/result')
def result():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('result.html')

# PAYMENT
@app.route('/pay', methods=['POST'])
def pay():
    if 'user' not in session:
        return redirect(url_for('login'))

    amount = float(request.form.get('amount', 100))

    new_payment = PaymentHistory(
        user_email=session['user'],
        amount=amount
    )

    db.session.add(new_payment)
    db.session.commit()

    flash("Payment successful (demo)", "success")
    return redirect(url_for('result'))

# DOWNLOAD REPORT (PDF)
@app.route('/download_report')
def download_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    paid = PaymentHistory.query.filter_by(user_email=session['user']).first()

    if not paid:
        flash("Please pay first", "warning")
        return redirect(url_for('result'))

    try:
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "EHR Health Report")

        c.setFont("Helvetica", 12)
        c.drawString(100, 720, f"User: {session['user']}")
        c.drawString(100, 700, f"Date: {datetime.utcnow()}")

        c.drawString(100, 670, "This is a demo health report.")

        c.save()
        buffer.seek(0)

        return send_file(buffer,
                         as_attachment=True,
                         download_name="report.pdf",
                         mimetype="application/pdf")

    except:
        return "Install reportlab first"

# HISTORY
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = PaymentHistory.query.filter_by(user_email=session['user']).all()
    return render_template('history.html', histories=data)

# DOWNLOAD CSV
@app.route('/download_history')
def download_history():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = PaymentHistory.query.filter_by(user_email=session['user']).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Amount", "Date"])

    for i in data:
        writer.writerow([i.id, i.amount, i.date])

    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()),
                     download_name="history.csv",
                     as_attachment=True,
                     mimetype="text/csv")

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for('login'))

# ---------------- RUN ----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)