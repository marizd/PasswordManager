import json
import hashlib
import getpass
import os
import pyperclip
import sys
from cryptography.fernet import Fernet
import smtplib
import pyotp
import qrcode
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Hashing function
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

# Encryption key generation and cipher setup
def generate_key():
    return Fernet.generate_key()

def initialize_cipher(key):
    return Fernet(key)

def encrypt_password(cipher, password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(cipher, encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

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
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # <- This is where it goes
            smtp.send_message(msg)
            print("[+] OTP sent to email.")
    except Exception as e:
        print("[-] Failed to send OTP:", e)

    return secret


# Register user and save credentials
def register(username, master_password):
    email = input("Enter your email address for MFA: ")
    hashed_master_password = hash_password(master_password)
    user_data = {
        'username': username,
        'master_password': hashed_master_password,
        'email': email
    }
    file_name = 'user_data.json'

    if os.path.exists(file_name) and os.path.getsize(file_name) == 0:
        with open(file_name, 'w') as file:
            json.dump(user_data, file)
            print("\n[+] Registration complete!\n")
    else:
        with open(file_name, 'x') as file:
            json.dump(user_data, file)
            print("\n[+] Registration complete!\n")

# Login and verify credentials + OTP
def login(username, entered_password):
    try:
        with open('user_data.json', 'r') as file:
            user_data = json.load(file)

        stored_password_hash = user_data.get('master_password')
        entered_password_hash = hash_password(entered_password)

        if entered_password_hash == stored_password_hash and username == user_data.get('username'):
            print("\n[+] Password verified.")

            # MFA with email OTP
            secret = send_otp(user_data.get("email"))
            totp = pyotp.TOTP(secret)
            code = input("Enter OTP sent to your email: ")

            if totp.verify(code):
                print("\n[+] OTP verified successfully. Login successful.\n")
            else:
                print("\n[-] Invalid OTP. Access denied.\n")
                sys.exit()
        else:
            print("\n[-] Invalid Login Credentials.\n")
            sys.exit()

    except Exception as e:
        print(f"\n[-] You have not registered or an error occurred: {e}\n")
        sys.exit()

# View saved websites
def view_websites():
    try:
        with open('passwords.json', 'r') as data:
            view = json.load(data)
        print("\nWebsites saved\n")
        for x in view:
            print(x['website'])
        print('\n')
    except FileNotFoundError:
        print("\n[-] You have not saved any passwords!\n")

# Add and save passwords
def add_password(website, password):
    if not os.path.exists('passwords.json'):
        data = []
    else:
        try:
            with open('passwords.json', 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = []

    encrypted_password = encrypt_password(cipher, password)
    password_entry = {'website': website, 'password': encrypted_password}
    data.append(password_entry)

    with open('passwords.json', 'w') as file:
        json.dump(data, file, indent=4)

# Retrieve saved passwords
def get_password(website):
    if not os.path.exists('passwords.json'):
        return None
    try:
        with open('passwords.json', 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = []

    for entry in data:
        if entry['website'] == website:
            return decrypt_password(cipher, entry['password'])
    return None

# Setup encryption key
key_filename = 'encryption_key.key'
if os.path.exists(key_filename):
    with open(key_filename, 'rb') as key_file:
        key = key_file.read()
else:
    key = generate_key()
    with open(key_filename, 'wb') as key_file:
        key_file.write(key)

cipher = initialize_cipher(key)

# Main loop
while True:
    print("1. Register")
    print("2. Login")
    print("3. Quit")
    choice = input("Enter your choice: ")

    if choice == '1':
        file = 'user_data.json'
        if os.path.exists(file) and os.path.getsize(file) > 0:
            print("\n[-] Master user already exists!!")
            sys.exit()
        else:
            username = input("Enter your username: ")
            master_password = getpass.getpass("Enter your master password: ")
            register(username, master_password)

    elif choice == '2':
        file = 'user_data.json'
        if os.path.exists(file):
            username = input("Enter your username: ")
            master_password = getpass.getpass("Enter your master password: ")
            login(username, master_password)
        else:
            print("\n[-] You have not registered. Please do that.\n")
            sys.exit()

        # Options after successful login
        while True:
            print("1. Add Password")
            print("2. Get Password")
            print("3. View Saved Websites")
            print("4. Quit")
            password_choice = input("Enter your choice: ")

            if password_choice == '1':
                website = input("Enter website: ")
                password = getpass.getpass("Enter password: ")
                add_password(website, password)
                print("\n[+] Password added!\n")

            elif password_choice == '2':
                website = input("Enter website: ")
                decrypted_password = get_password(website)
                if website and decrypted_password:
                    pyperclip.copy(decrypted_password)
                    print(f"\n[+] Password for {website}: {decrypted_password}\n[+] Password copied to clipboard.\n")
                else:
                    print("\n[-] Password not found! Did you save it?\n")

            elif password_choice == '3':
                view_websites()

            elif password_choice == '4':
                break

    elif choice == '3':
        break
