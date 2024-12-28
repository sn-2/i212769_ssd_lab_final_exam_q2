import unittest
from main import app
import time

class TestRateLimits(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_rate_limit(self):
        """Test that login is limited to 5 requests per minute"""
        # Make 5 requests (should succeed)
        for i in range(5):
            response = self.app.post('/login', data={'username': 'test', 'password': 'test'})
            self.assertNotEqual(response.status_code, 429)  # 429 is Too Many Requests
        
        # 6th request should be rate limited
        response = self.app.post('/login', data={'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 429)

    def test_ping_rate_limit(self):
        """Test that ping is limited to 10 requests per minute"""
        # Make 10 requests (should succeed)
        for i in range(10):
            response = self.app.get('/ping?ip=127.0.0.1')
            self.assertNotEqual(response.status_code, 429)
        
        # 11th request should be rate limited
        response = self.app.get('/ping?ip=127.0.0.1')
        self.assertEqual(response.status_code, 429)

    def test_search_rate_limit(self):
        """Test that search is limited to 20 requests per minute"""
        # Make 20 requests (should succeed)
        for i in range(20):
            response = self.app.get('/search?q=test')
            self.assertNotEqual(response.status_code, 429)
        
        # 21st request should be rate limited
        response = self.app.get('/search?q=test')
        self.assertEqual(response.status_code, 429)

    def test_comment_rate_limit(self):
        """Test that comment is limited to 10 requests per minute"""
        # Make 10 requests (should succeed)
        for i in range(10):
            response = self.app.post('/comment', data={'comment': 'test comment'})
            self.assertNotEqual(response.status_code, 429)
        
        # 11th request should be rate limited
        response = self.app.post('/comment', data={'comment': 'test comment'})
        self.assertEqual(response.status_code, 429)

    def test_admin_delete_rate_limit(self):
        """Test that admin delete is limited to 3 requests per minute"""
        # Make 3 requests (should succeed)
        for i in range(3):
            response = self.app.post('/admin/delete_user/1')
            self.assertNotEqual(response.status_code, 429)
        
        # 4th request should be rate limited
        response = self.app.post('/admin/delete_user/1')
        self.assertEqual(response.status_code, 429)

if __name__ == '__main__':
    unittest.main()
