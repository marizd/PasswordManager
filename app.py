from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from logic import register, login, add_password, get_password, view_websites, load_passwords, save_passwords, encrypt_password

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
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_route'))
    websites = view_websites()
    site_data = {entry['website']: {'username': 'user@example.com'} for entry in load_passwords()}
    return render_template('dashboard.html', websites=websites, site_data=site_data)

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

@app.route('/delete/<website>', methods=['POST'])
def delete_password(website):
    data = load_passwords()
    data = [entry for entry in data if entry['website'] != website]
    save_passwords(data)
    return jsonify({'success': True})

@app.route('/edit/<website>', methods=['POST'])
def edit_password(website):
    new_password = request.form.get('new_password')
    data = load_passwords()
    for entry in data:
        if entry['website'] == website:
            entry['password'] = encrypt_password(new_password)
            break
    save_passwords(data)
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login_route'))

if __name__ == '__main__':
    app.run(debug=True)
