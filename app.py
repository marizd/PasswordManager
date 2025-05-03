from flask import Flask, render_template, request, redirect, session, flash, url_for
from logic import register, login, add_password, get_password, view_websites, send_otp, verify_otp

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_route'))

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register(username, password):
            flash('Registered successfully! Please log in.', 'success')
            return redirect(url_for('login_route'))
        flash('User already exists!', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login(username, password):
            session['username'] = username
            session['otp_secret'] = send_otp("your@email.com")  # Replace with dynamic email if implemented
            return redirect(url_for('verify_otp_route'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_route():
    if request.method == 'POST':
        code = request.form['otp']
        if verify_otp(session.get('otp_secret', ''), code):
            flash('OTP verified. Welcome!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid OTP.', 'danger')
    return render_template('verify_otp.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_route'))
    websites = view_websites()
    return render_template('dashboard.html', websites=websites)

@app.route('/add', methods=['POST'])
def add():
    website = request.form['website']
    password = request.form['password']
    add_password(website, password)
    return redirect(url_for('dashboard'))

@app.route('/get', methods=['POST'])
def retrieve():
    website = request.form['website']
    password = get_password(website)
    websites = view_websites()
    return render_template('dashboard.html', password=password, site=website, websites=websites)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login_route'))

if __name__ == '__main__':
    app.run(debug=True)
