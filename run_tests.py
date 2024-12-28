import unittest
import sys

# Import all test modules
from test_security_headers import TestSecurityHeaders
from test_logging import TestLogging
from test_rate_limits import TestRateLimits
from test_xss_protection import TestXSSProtection

def run_tests():
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSecurityHeaders))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogging))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRateLimits))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXSSProtection))
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
