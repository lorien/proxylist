from __future__ import annotations

import pytest
from test_server import Response, TestServer

from proxylist.errors import ProxySourceReadError
from proxylist.source import NetworkFileProxySource


def test_url_error() -> None:
    serv = TestServer()
    try:
        serv.start()
        serv.add_response(
            Response(raw_callback=lambda: b"You shall not pass!"), count=10
        )
        with pytest.raises(ProxySourceReadError):
            NetworkFileProxySource(serv.get_url()).load_content()
    finally:
        serv.stop()
