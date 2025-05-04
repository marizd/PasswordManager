import unittest
import os
from password_manager import register, login, add_password, get_password

class TestPasswordManagerIntegration(unittest.TestCase):

    def setUp(self):
        # Remove old files for clean test
        for f in ['user_data.json', 'passwords.json']:
            if os.path.exists(f):
                os.remove(f)

    def test_full_flow(self):
        # Register user
        self.assertTrue(register("testuser", "password123"))
        
        # Login with skip_otp=True for testing
        self.assertTrue(login("testuser", "password123", skip_otp=True))

        # Add and retrieve password
        add_password("example.com", "mysecurepassword")
        retrieved = get_password("example.com")
        self.assertEqual(retrieved, "mysecurepassword")

    def tearDown(self):
        for f in ['user_data.json', 'passwords.json']:
            if os.path.exists(f):
                os.remove(f)

if __name__ == '__main__':
    unittest.main()
