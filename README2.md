TEST CASES FOR PASSWORD MANAGER

Web Interface Test Cases
    1. Login Functionality
    - Test valid credentials (username: test1, password: hello)
    - Test invalid credentials
    - Verify redirect to dashboard after successful login

    2. Dashboard Access
    - Verify dashboard loads correctly after login
    - Test dashboard access without login (should redirect to login)

    3. Password Addition
    - Add a new password entry with website and password
    - Verify the new entry appears in the password list
    - Test adding a duplicate website entry
    
    4. Storage Security
    - Verify passwords are stored encrypted in passwords.json
    - Ensure master password is properly hashed in user_data.json

Command-Line Interface Test Cases
    1. Login Authentication
    - Test valid login credentials
    - Test invalid username or password
    *Note: Registration functionality is currently unavailable in command-line mode
    
    2. MFA Functionality
    - Test email OTP delivery
    - Verify correct OTP grants access
    - Verify incorrect OTP denies access
    * Important: Before testing, manually replace username in user_data.json with your email to receive OTP
    
    3. Password Management
    - Test adding passwords for different websites
    - Test retrieving passwords by website name
    - Verify passwords are correctly copied to clipboard
    - View all saved websites
    
    4. Data Encryption
    - Verify passwords are stored in encrypted format
    - Test decryption functionality
    - Verify key persistence across sessions


Manual Setup for Command-Line Testing
Since registration does not work in command-line mode at the moment:
    1. Ensure user_data.json exists with valid credentials structure:
    - {"username": "your-email@example.com", "master_password": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"}
    * It should look like this!
    * Important: You only need to change the email, not the hashed password. For our current testin purposes, the password will always be 'hello'

    2. Run the password manager:
    - python password_manager.py

    3. Select the login option (2) and use the credentials matching those in user_data.json
    
    4. Check that OTP is delivered to the email specified in user_data.json
    
    5. Test all password management functions after successful authentication
    
    6. Verify data storage in passwords.json and encryption_key.key