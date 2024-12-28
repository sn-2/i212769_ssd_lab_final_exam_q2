import unittest
from main import app
import json

class TestXSSProtection(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_csp_headers_present(self):
        """Test that CSP headers are present in response"""
        response = self.app.get('/')
        self.assertIn('Content-Security-Policy', response.headers)
        
        # Verify CSP policies
        csp = response.headers['Content-Security-Policy']
        self.assertIn("default-src 'none'", csp)
        self.assertIn("style-src 'self'", csp)
        self.assertIn("script-src 'none'", csp)
        self.assertIn("form-action 'self'", csp)
    
    def test_xss_in_comments(self):
        """Test that script injection in comments is prevented"""
        # Try to inject a script
        malicious_comment = "<script>alert('xss')</script>"
        response = self.app.post('/comment', data={'comment': malicious_comment})
        
        # Get the page and check if script is escaped in comments
        response = self.app.get('/')
        response_str = response.data.decode('utf-8')
        comments_section = response_str[response_str.find('<div id="comments">'):]
        
        # Convert back to bytes for assertion
        comments_section = comments_section.encode('utf-8')
        
        # Verify script is escaped in comments section
        self.assertIn(b'&lt;script&gt;', comments_section)
        self.assertNotIn(b'<script>', comments_section)
    
if __name__ == '__main__':
    unittest.main()
