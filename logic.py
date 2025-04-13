import json, os, hashlib
from cryptography.fernet import Fernet

# ---------🔐 Encryption & Decryption Setup ----------

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

# ---------🔐 Master Password Logic ----------

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

def register(username, master_password):
    file = 'user_data.json'
    if os.path.exists(file) and os.path.getsize(file) != 0:
        return False  # Already registered

    hashed_pw = hash_password(master_password)
    user_data = {'username': username, 'master_password': hashed_pw}
    with open(file, 'w') as f:
        json.dump(user_data, f)
    return True

def login(username, entered_password):
    try:
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
        return (
            username == user_data['username'] and
            hash_password(entered_password) == user_data['master_password']
        )
    except Exception:
        return False

# ---------🔐 Password Management ----------

def add_password(website, password, username=""):
    filename = 'passwords.json'
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    encrypted_pw = encrypt_password(password)
    
    # Check if website exists and update it
    for entry in data:
        if entry['website'] == website:
            entry['password'] = encrypted_pw
            entry['username'] = username
            break
    else:
        # Website doesn't exist, append new entry
        data.append({
            'website': website, 
            'password': encrypted_pw,
            'username': username
        })

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_password(website):
    if not os.path.exists('passwords.json'):
        return None
    try:
        with open('passwords.json', 'r') as f:
            data = json.load(f)
        for entry in data:
            if entry['website'] == website:
                return decrypt_password(entry['password'])
    except json.JSONDecodeError:
        pass
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

def delete_password(website):
    if not os.path.exists('passwords.json'):
        return False
    try:
        with open('passwords.json', 'r') as f:
            data = json.load(f)
        
        # Find and remove the website entry
        filtered_data = [entry for entry in data if entry['website'] != website]
        
        # If no entries were removed, return False
        if len(filtered_data) == len(data):
            return False
            
        with open('passwords.json', 'w') as f:
            json.dump(filtered_data, f, indent=4)
            
        return True
    except json.JSONDecodeError:
        return False