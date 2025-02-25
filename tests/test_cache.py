"""
Tests for cache

To run all tests in suite from commandline:
   python -m unittest tests.cache

Specific test class:
   python -m unittest tests.cache.TestCache

"""
from unittest import TestSuite

from tests.context import yfinance as yf

import unittest
import tempfile
import os


class TestCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempCacheDir = tempfile.TemporaryDirectory()
        yf.set_tz_cache_location(cls.tempCacheDir.name)

    @classmethod
    def tearDownClass(cls):
        yf.cache._TzDBManager.close_db()
        cls.tempCacheDir.cleanup()

    def test_storeTzNoRaise(self):
        # storing TZ to cache should never raise exception
        tkr = 'AMZN'
        tz1 = "America/New_York"
        tz2 = "London/Europe"
        cache = yf.cache.get_tz_cache()
        cache.store(tkr, tz1)
        cache.store(tkr, tz2)

    def test_setTzCacheLocation(self):
        self.assertEqual(yf.cache._TzDBManager.get_location(), self.tempCacheDir.name)

        tkr = 'AMZN'
        tz1 = "America/New_York"
        cache = yf.cache.get_tz_cache()
        cache.store(tkr, tz1)

        self.assertTrue(os.path.exists(os.path.join(self.tempCacheDir.name, "tkr-tz.db")))


class TestCacheNoPermission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name == "nt":  # Windows
            cls.cache_path = "C:\\Windows\\System32\\yf-cache"
        else:  # Unix/Linux/MacOS
            # Use a writable directory
            cls.cache_path = "/yf-cache"
        yf.set_tz_cache_location(cls.cache_path)

    def test_tzCacheRootStore(self):
        # Test that if cache path in read-only filesystem, no exception.
        tkr = 'AMZN'
        tz1 = "America/New_York"

        # During attempt to store, will discover cannot write
        yf.cache.get_tz_cache().store(tkr, tz1)

        # Handling the store failure replaces cache with a dummy
        cache = yf.cache.get_tz_cache()
        self.assertTrue(cache.dummy)
        cache.store(tkr, tz1)

    def test_tzCacheRootLookup(self):
        # Test that if cache path in read-only filesystem, no exception.
        tkr = 'AMZN'
        # During attempt to lookup, will discover cannot write
        yf.cache.get_tz_cache().lookup(tkr)

        # Handling the lookup failure replaces cache with a dummy
        cache = yf.cache.get_tz_cache()
        self.assertTrue(cache.dummy)
        cache.lookup(tkr)

def suite():
    ts: TestSuite = unittest.TestSuite()
    ts.addTest(TestCache('Test cache'))
    ts.addTest(TestCacheNoPermission('Test cache no permission'))
    return ts


if __name__ == '__main__':
    unittest.main()
