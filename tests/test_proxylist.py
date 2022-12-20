import os
import tempfile
from unittest import TestCase

from test_server import Response, TestServer

from proxylist import ProxyList

DEFAULT_PROXY_LIST_DATA = b"""
'1.1.1.1:8080
'1.1.1.2:8080
"""


class ProxyListTestCase(TestCase):
    server: TestServer

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = TestServer()
        cls.server.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()

    def setUp(self) -> None:
        self.server.reset()

    def generate_plist_file(self, data: bytes) -> str:
        df, path = tempfile.mkstemp()
        os.close(df)
        with open(path, "wb") as out:
            out.write(data)
        return path

    def test_basic(self) -> None:
        pl = ProxyList()
        self.assertEqual(0, pl.size())

    def test_file_proxy_source(self) -> None:
        pl = ProxyList()
        path = self.generate_plist_file(DEFAULT_PROXY_LIST_DATA)
        try:
            pl.load_file(path)
            self.assertEqual(2, pl.size())
        finally:
            os.unlink(path)

    def test_web_proxy_source(self) -> None:
        pl = ProxyList()
        self.server.add_response(Response(data=DEFAULT_PROXY_LIST_DATA))
        pl.load_url(self.server.get_url())
        self.assertEqual(2, pl.size())

    def test_get_next_proxy(self) -> None:
        pl = ProxyList()
        path = self.generate_plist_file(b"foo:1\nbar:1")
        pl.load_file(path)
        self.assertEqual(pl.get_next_proxy().host, "foo")
        self.assertEqual(pl.get_next_proxy().host, "bar")
        self.assertEqual(pl.get_next_proxy().host, "foo")
        pl.load_file(path)
        self.assertEqual(pl.get_next_proxy().host, "foo")
        os.unlink(path)
