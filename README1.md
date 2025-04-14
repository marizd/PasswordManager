Overview:
PasswordManager is a secure password storage application with both a web interface and command-line functionality. The project currently has a functional front-end website with basic features and additional backend capabilities that are being integrated.

Current Features:
- Web Interface: Run *python app.py* after installing required libraries
    -   Login page (use username: test1, password: hello)
    -   Dashboard for adding new passwords

-   Command-line Interface: Run *python password_manager.py* after installing required libraries
    -   Account registration
    -   Two-factor authentication (2FA) via email OTP
    -   Password storage and retrieval

Coming Soon in the Next Phase:
-   Password editing and deletion in web interface
-   Full MFA integration with the web interface
-   Enhanced dashboard functionality

Install the Following Required Libraries:
-   Python 3.x
-   Flask *pip install flask*
-   Cryptography library *pip install cryptography*
-   Pyperclip

Setup Instructions:
1. Clone or download the project folder
2. Open terminal and navigate to project directory
3. Install required packages: pip install flask cryptography pyperclip
4. Run the web interface:
    -   python app.py
    -   OR run the command-line version: python password_manager.py
5. Follow on-screen instructions to register, login, add passwords, and retrieve them

Default Web Login:
Username: test1
Password: hello

Important Note for Testing MFA:
To test the command-line MFA functionality temporarily, you will need to:
1. Open the user_data.json file insead of registering
2. Replace the username with your own email address
3. Save and run the application again and proceed with login
4. The OTP will be sent to the email address you specified