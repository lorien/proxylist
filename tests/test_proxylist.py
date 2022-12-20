import os
import tempfile
from unittest import TestCase

import pytest
from test_server import Response, TestServer

from proxylist import ProxyList
from proxylist.source import ListProxySource

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

    def test_constructor(self) -> None:
        plist = ProxyList(ListProxySource(["foo:88"]))
        self.assertEqual(plist.size(), 1)

    def test_file_proxy_source(self) -> None:
        path = self.generate_plist_file(DEFAULT_PROXY_LIST_DATA)
        try:
            plist = ProxyList.create_from_file(path)
            self.assertEqual(2, plist.size())
        finally:
            os.unlink(path)

    def test_web_proxy_source(self) -> None:
        self.server.add_response(Response(data=DEFAULT_PROXY_LIST_DATA))
        plist = ProxyList.create_from_url(self.server.get_url())
        self.assertEqual(2, plist.size())

    def test_get_next_server(self) -> None:
        path = self.generate_plist_file(b"foo:1\nbar:1")
        plist = ProxyList.create_from_file(path)
        self.assertEqual(plist.get_next_server().host, "foo")
        self.assertEqual(plist.get_next_server().host, "bar")
        self.assertEqual(plist.get_next_server().host, "foo")
        plist = ProxyList.create_from_file(path)
        self.assertEqual(plist.get_next_server().host, "foo")
        os.unlink(path)

    def test_create_from_list(self) -> None:
        plist = ProxyList.create_from_list(["foo:1", "bar:2"])
        self.assertEqual(plist.get_next_server().host, "foo")

    def test_get_random_server(self) -> None:
        plist = ProxyList.create_from_list(["foo:1", "bar:2"])
        self.assertEqual(
            {plist.get_random_server().host for _ in range(10)}, {"foo", "bar"}
        )

    def test_iter_interface(self) -> None:
        plist = ProxyList.create_from_list(["foo:1"])
        self.assertEqual(next(iter(plist)).host, "foo")

    def test_len(self) -> None:
        plist = ProxyList.create_from_list(["foo:1", "bar:2"])
        self.assertEqual(len(plist), 2)

    def test_getitem(self) -> None:
        plist = ProxyList.create_from_list(["foo:1", "bar:2"])
        self.assertEqual(plist[0].host, "foo")
        self.assertEqual(plist[1].host, "bar")
        with pytest.raises(IndexError):
            self.assertEqual(plist[2].host, "bar")
