#!/usr/bin/env python
from unittest import TestCase
import unittest
import tempfile
import os

from proxylist import ProxyList
from test_server import TestServer

DEFAULT_PROXY_LIST_DATA = '''
'1.1.1.1:8080
'1.1.1.2:8080
'''


class ProxyListTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = TestServer()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.server.reset()

    def generate_plist_file(self, data):
        df, path = tempfile.mkstemp()
        with open(path, 'w') as out:
            out.write(data)
        return path

    def test_basic(self):
        pl = ProxyList()
        self.assertEqual(0, pl.size())

    def test_file_proxy_source(self):
        pl = ProxyList()
        path = self.generate_plist_file(DEFAULT_PROXY_LIST_DATA)
        pl.load_file(path)
        self.assertEqual(2, pl.size())
        os.unlink(path)

    def test_web_proxy_source(self):
        pl = ProxyList()
        self.server.response['data'] = DEFAULT_PROXY_LIST_DATA
        pl.load_url(self.server.get_url())
        self.assertEqual(2, pl.size())

    def test_get_next_proxy(self):
        pl = ProxyList()
        path = self.generate_plist_file('foo:1\nbar:1')
        pl.load_file(path)
        self.assertEqual(pl.next().host, 'foo')
        self.assertEqual(pl.next().host, 'bar')
        self.assertEqual(pl.next().host, 'foo')
        pl.load_file(path)
        self.assertEqual(pl.next().host, 'foo')
        os.unlink(path)


if __name__ == '__main__':
    unittest.main()
