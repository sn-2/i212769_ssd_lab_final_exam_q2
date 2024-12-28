import unittest
import os
from main import app
from datetime import datetime

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.log_file = f'logs/security_{datetime.now().strftime("%Y%m%d")}.log'
        
    def test_security_header_logging(self):
        # Make a request to trigger security header logging
        response = self.app.get('/')
        
        # Verify log file exists
        self.assertTrue(os.path.exists(self.log_file))
        
        # Read the log file
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        # Check if security header logging is present
        self.assertIn('Security headers set for request', log_content)
        self.assertIn('from 127.0.0.1', log_content)
        
    def test_rate_limit_logging(self):
        # Make multiple requests to trigger rate limit
        for _ in range(6):  # Login endpoint has 5/minute limit
            self.app.post('/login', data={'username': 'test', 'password': 'test'})
            
        # Read the log file
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            
        # Check if rate limit logging is present
        self.assertIn('Rate limit exceeded', log_content)
        self.assertIn('Login attempt from', log_content)

if __name__ == '__main__':
    unittest.main()
