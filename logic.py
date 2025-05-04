import json
import os
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

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

def load_users():
    if not os.path.exists('user_data.json'):
        return []
    with open('user_data.json', 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open('user_data.json', 'w') as f:
        json.dump(users, f, indent=4)

def register(username, password):
    users = load_users()
    if any(u['username'] == username for u in users):
        return False

    hashed_pw = hash_password(password)
    users.append({'username': username, 'master_password': hashed_pw})
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    for u in users:
        if u['username'] == username and u['master_password'] == hash_password(password):
            return True
    return False

# ---------------- Password Management ----------------

def load_passwords():
    if not os.path.exists('passwords.json'):
        return []
    with open('passwords.json', 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_passwords(data):
    with open('passwords.json', 'w') as f:
        json.dump(data, f, indent=4)

def add_password(website, password):
    data = load_passwords()
    encrypted_pw = encrypt_password(password)
    data.append({'website': website, 'password': encrypted_pw})
    save_passwords(data)

def get_password(website):
    data = load_passwords()
    for entry in data:
        if entry['website'] == website:
            return decrypt_password(entry['password'])
    return None

def view_websites():
    data = load_passwords()
    return [entry['website'] for entry in data]
