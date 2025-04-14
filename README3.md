Unit Testing Instructions

1. make sure the main code files and test_manager.py are in the same directory
2. open the terminal and navigate to the project directory
3. run the following test: python -m unittest test_password_manager.py
This test confirms registration/login, password encryption/decryption, and adding/retrieving passwords is functionable

test_password_manager.py

import unittest
import os
from password_manager import hash_password, encrypt_password, decrypt_password, add_password, get_password, initialize_cipher, generate_key

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        self.test_key = generate_key()
        self.cipher = initialize_cipher(self.test_key)

    def test_hash_password(self):
        hashed = hash_password("securepassword")
        self.assertEqual(len(hashed), 64)

    def test_encrypt_decrypt_password(self):
        original = "mypassword123"
        encrypted = encrypt_password(self.cipher, original)
        decrypted = decrypt_password(self.cipher, encrypted)
        self.assertEqual(original, decrypted)

    def test_add_and_get_password(self):
        website = "testsite.com"
        password = "Test123!"
        add_password(website, password)
        retrieved = get_password(website)
        self.assertEqual(password, retrieved)

if __name__ == '__main__':
    unittest.main()
