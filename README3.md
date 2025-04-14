Unit Testing Instructions

Overview:
The test suite verifies the core functionality of the password management system including password hashing, encryption/decryption, and storage/retrieval operations.

Test File Contents
1. The test_password_manager.py file includes tests for the following functions:
    - hash_password: Tests that passwords are properly hashed
    - encrypt_password and decrypt_password: Tests encryption and decryption functionality
    - add_password and get_password: Tests storing and retrieving passwords

Prerequisites:
Before running the tests, ensure you have:
    - Python 3.x installed
    - The Password Manager application files
    - Required dependencies installed: pip install cryptography pyperclip

Running the Tests:
To run the tests, simply execute the test file directly with Python:
    - python test_password_manager.py

What the Tests Verify:
1. Password Hashing: Ensures the hashing function produces a 64-character hex string
2. Encryption/Decryption: Tests that passwords can be encrypted and then correctly decrypted
3. Storage & Retrieval: Confirms that passwords can be saved and later retrieved accurately

Important Notes:
1. The tests use temporary encryption keys generated during test execution
2. Tests will interact with the regular password storage files (passwords.json), so back up any existing files before testing
3. Make sure the Password Manager application is in the same directory as the test file
