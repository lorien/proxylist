from __future__ import annotations

from typing import Any

import pytest
from test_server import Response, TestServer

from proxylist.errors import ProxySourceReadError
from proxylist.source import (
    LinesListProxySource,
    LocalFileProxySource,
    NetworkFileProxySource,
)


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


@pytest.mark.parametrize(
    "source,inp",
    [
        (LinesListProxySource, "var/proxy.txt"),
        (LocalFileProxySource, "https://example.com/proxy.txt"),
        (NetworkFileProxySource, ["server:88"]),
    ],
)
def test_positional_parameters(source: type[Any], inp: str | list[str]) -> None:
    with pytest.raises(TypeError) as ex:
        source(inp, "socks5")
    assert "takes 2 positional" in str(ex.value)
