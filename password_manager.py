import json, hashlib, getpass, os, pyperclip, sys
import smtplib
import pyotp
import qrcode
from cryptography.fernet import Fernet
from email.message import EmailMessage
from dotenv import load_dotenv

# Load email credentials from .env
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ---------------- Encryption Setup ---------------- #
def generate_key():
    return Fernet.generate_key()

def load_or_create_key():
    key_file = 'encryption_key.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    key = generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)
    return key

cipher = Fernet(load_or_create_key())

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# ---------------- Hashing ---------------- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- OTP ---------------- #
def send_otp(email, secret, skip=False):
    if skip:
       
        return

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
            print("[+] OTP sent to email.")
    except Exception as e:
        print("[-] Failed to send OTP:", e)
        return

# ---------------- User Logic ---------------- #
def load_users():
    if not os.path.exists('user_data.json'):
        return {}
    with open('user_data.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('user_data.json', 'w') as f:
        json.dump(users, f, indent=4)

def register(username, master_password):
    users = load_users()
    if username in users:
        print("[-] Username already exists.")
        return False

    email = input("Enter your email for MFA: ")
    otp_secret = pyotp.random_base32()
    users[username] = {
        "master_password": hash_password(master_password),
        "email": email,
        "otp_secret": otp_secret
    }
    save_users(users)
    print("[+] Registration complete!")
    return True

def login(username, entered_password, skip_otp=False):
    users = load_users()
    user = users.get(username)
    if not user or hash_password(entered_password) != user['master_password']:
        print("[-] Invalid username or password.")
        return False

    print("[+] Password verified.")
    send_otp(user['email'], user['otp_secret'], skip=skip_otp)

    if skip_otp:
        return True  # Skip OTP prompt in tests

    code = input("Enter OTP sent to your email: ")
    if pyotp.TOTP(user['otp_secret']).verify(code):
        print("[+] OTP verified. Login successful.")
        return True
    else:
        print("[-] Invalid OTP.")
        return False

# ---------------- Password Management ---------------- #
def load_passwords():
    if not os.path.exists('passwords.json'):
        return []
    with open('passwords.json', 'r') as f:
        return json.load(f)

def save_passwords(data):
    with open('passwords.json', 'w') as f:
        json.dump(data, f, indent=4)

def add_password(website, password):
    data = load_passwords()
    encrypted_pw = encrypt_password(password)
    data.append({'website': website, 'password': encrypted_pw})
    save_passwords(data)
    print("[+] Password added.")

def get_password(website):
    data = load_passwords()
    for entry in data:
        if entry['website'] == website:
            return decrypt_password(entry['password'])
    return None

def view_websites():
    data = load_passwords()
    print("\nWebsites saved:")
    for entry in data:
        print("-", entry['website'])
    print()

# ---------------- Main Menu ---------------- #
if __name__ == '__main__':
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter username: ")
            master_password = getpass.getpass("Enter master password: ")
            register(username, master_password)

        elif choice == '2':
            username = input("Enter username: ")
            master_password = getpass.getpass("Enter master password: ")
            if login(username, master_password):
                while True:
                    print("\n1. Add Password")
                    print("2. Get Password")
                    print("3. View Websites")
                    print("4. Logout")
                    option = input("Select an option: ")

                    if option == '1':
                        website = input("Enter website: ")
                        password = getpass.getpass("Enter password: ")
                        add_password(website, password)

                    elif option == '2':
                        website = input("Enter website to retrieve: ")
                        pw = get_password(website)
                        if pw:
                            pyperclip.copy(pw)
                            print(f"Password: {pw} (copied to clipboard)")
                        else:
                            print("[-] Password not found.")

                    elif option == '3':
                        view_websites()

                    elif option == '4':
                        break

        elif choice == '3':
            print("Exiting...")
            break

        else:
            print("[-] Invalid option.")
