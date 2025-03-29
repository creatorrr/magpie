#!/usr/bin/env python
"""
Simple test runner for Magpie library.
Use this script to run tests from the command line.
"""

import sys
import unittest

if __name__ == "__main__":
    # Discover and run all tests
    test_suite = unittest.defaultTestLoader.discover("tests")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Return non-zero exit code if tests fail
    sys.exit(not result.wasSuccessful())
