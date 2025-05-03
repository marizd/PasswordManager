import json
import os
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import pyotp
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ---------------- Encryption Setup ----------------

def generate_key():
    return Fernet.generate_key()

def initialize_cipher():
    key_file = 'encryption_key.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()
    else:
        key = generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
    return Fernet(key)

cipher = initialize_cipher()

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# ---------------- Hashing and User Handling ----------------

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

def register(username, password):
    users = []
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = []

        if any(u['username'] == username for u in users):
            return False

    hashed_pw = hash_password(password)
    users.append({'username': username, 'master_password': hashed_pw})

    with open('user_data.json', 'w') as f:
        json.dump(users, f, indent=4)

    return True

def login(username, password):
    if not os.path.exists('user_data.json'):
        return False

    with open('user_data.json', 'r') as f:
        users = json.load(f)
        for u in users:
            if u['username'] == username and u['master_password'] == hash_password(password):
                return True

    return False

# ---------------- OTP Email MFA ----------------

def send_otp(email):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    otp = totp.now()

    msg = EmailMessage()
    msg.set_content(f"Your OTP is: {otp}")
    msg['Subject'] = 'Your Login OTP'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return secret
    except Exception as e:
        print("Failed to send OTP:", e)
        return None

def verify_otp(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

# ---------------- Password Management ----------------

def add_password(website, password):
    if os.path.exists('passwords.json'):
        try:
            with open('passwords.json', 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    encrypted_pw = encrypt_password(password)
    data.append({'website': website, 'password': encrypted_pw})

    with open('passwords.json', 'w') as f:
        json.dump(data, f, indent=4)

def get_password(website):
    if not os.path.exists('passwords.json'):
        return None

    with open('passwords.json', 'r') as f:
        data = json.load(f)
        for entry in data:
            if entry['website'] == website:
                return decrypt_password(entry['password'])
    return None

def view_websites():
    if not os.path.exists('passwords.json'):
        return []
    try:
        with open('passwords.json', 'r') as f:
            data = json.load(f)
        return [entry['website'] for entry in data]
    except json.JSONDecodeError:
        return []
