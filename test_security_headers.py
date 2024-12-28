import unittest
from main import app

class TestSecurityHeaders(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        
    def test_xframe_options_header(self):
        # Make a request to the root endpoint
        response = self.app.get('/')
        
        # Check if X-Frame-Options header exists and is set to SAMEORIGIN
        self.assertIn('X-Frame-Options', response.headers)
        self.assertEqual(response.headers['X-Frame-Options'], 'SAMEORIGIN')

if __name__ == '__main__':
    unittest.main()
