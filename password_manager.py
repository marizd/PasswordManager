import json
import hashlib
import getpass
import os
import pyperclip
import sys
import smtplib
import pyotp
from cryptography.fernet import Fernet
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --------- Hashing ---------
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

# --------- Encryption ---------
def generate_key():
    return Fernet.generate_key()

def initialize_cipher(key):
    return Fernet(key)

def encrypt_password(cipher, password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(cipher, encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# --------- OTP Email ---------
def send_otp(email):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    otp = totp.now()

    msg = EmailMessage()
    msg.set_content(f"Your OTP is: {otp}")
    msg["Subject"] = "Your Login OTP"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("[+] OTP sent to email.")
    except Exception as e:
        print("[-] Failed to send OTP:", e)

    return secret

# --------- User Registration ---------
def register(username, master_password):
    email = input("Enter your email address for MFA: ")
    hashed_master_password = hash_password(master_password)
    user_data = {
        "username": username,
        "master_password": hashed_master_password,
        "email": email
    }
    file_name = "user_data.json"

    if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
        with open(file_name, "w") as file:
            json.dump(user_data, file)
            print("\n[+] Registration complete!\n")
    else:
        print("\n[-] User already exists.\n")

# --------- User Login ---------
def login(username, entered_password):
    try:
        with open("user_data.json", "r") as file:
            user_data = json.load(file)

        stored_password_hash = user_data.get("master_password")
        entered_password_hash = hash_password(entered_password)

        if entered_password_hash == stored_password_hash and username == user_data.get("username"):
            print("\n[+] Password verified.")

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

# --------- Password Storage ---------
key_filename = "encryption_key.key"
if os.path.exists(key_filename):
    with open(key_filename, "rb") as key_file:
        key = key_file.read()
else:
    key = generate_key()
    with open(key_filename, "wb") as key_file:
        key_file.write(key)

cipher = initialize_cipher(key)

def add_password(website, password):
    filename = "passwords.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    encrypted_pw = encrypt_password(cipher, password)
    data.append({"website": website, "password": encrypted_pw})

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_password(website):
    if not os.path.exists("passwords.json"):
        return None
    try:
        with open("passwords.json", "r") as f:
            data = json.load(f)
        for entry in data:
            if entry["website"] == website:
                return decrypt_password(cipher, entry["password"])
    except json.JSONDecodeError:
        pass
    return None

def view_websites():
    if not os.path.exists("passwords.json"):
        print("\n[-] You have not saved any passwords!\n")
        return
    try:
        with open("passwords.json", "r") as f:
            data = json.load(f)
        print("\nWebsites saved:")
        for entry in data:
            print(entry["website"])
        print()
    except json.JSONDecodeError:
        print("\n[-] Error reading saved passwords.\n")

# --------- CLI Entry Point ---------
if __name__ == "__main__":
    while True:
        print("1. Register")
        print("2. Login")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter your username: ")
            master_password = getpass.getpass("Enter your master password: ")
            register(username, master_password)

        elif choice == "2":
            username = input("Enter your username: ")
            master_password = getpass.getpass("Enter your master password: ")
            login(username, master_password)

            while True:
                print("1. Add Password")
                print("2. Get Password")
                print("3. View Saved Websites")
                print("4. Logout")
                sub_choice = input("Enter your choice: ")

                if sub_choice == "1":
                    site = input("Enter website: ")
                    pw = getpass.getpass("Enter password: ")
                    add_password(site, pw)
                    print("[+] Password added!\n")

                elif sub_choice == "2":
                    site = input("Enter website: ")
                    pw = get_password(site)
                    if pw:
                        pyperclip.copy(pw)
                        print(f"[+] Password: {pw}\n[+] Copied to clipboard.\n")
                    else:
                        print("[-] Password not found.\n")

                elif sub_choice == "3":
                    view_websites()

                elif sub_choice == "4":
                    break

        elif choice == "3":
            break
