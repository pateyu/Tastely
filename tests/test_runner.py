import pytest
import os

def run_all_tests():
    """Run tests from test_route.py"""
    test_file = os.path.join(os.path.dirname(__file__), "test_route.py")
    return pytest.main([test_file])
