import pytest

from proxylist.errors import InvalidProxyLine
from proxylist.parser import ProxyListParser
from proxylist.server import ProxyServer


def test_parse_proxy_line_basic() -> None:
    assert ProxyListParser.parse_proxy_line("foo:88") == ("foo", 88, None, None)


def test_parse_proxy_line_userpwd() -> None:
    assert ProxyListParser.parse_proxy_line("foo:88:user:pwd") == (
        "foo",
        88,
        "user",
        "pwd",
    )


def test_parse_proxy_line_invlalid() -> None:
    with pytest.raises(InvalidProxyLine):
        ProxyListParser.parse_proxy_line("zzz")


def test_parse_raw_list_data() -> None:
    items = list(
        ProxyListParser.parse_raw_list_data(
            "invalid-line\nfoo:88\nbar:99:user:pwd",
            proxy_type="socks5",
            # proxy_userpwd="xuser:xpwd",
        )
    )
    assert items[0] == ProxyServer("foo", 88, None, None, "socks5")
    assert items[1] == ProxyServer("bar", 99, "user", "pwd", "socks5")


def test_parse_raw_list_data_defined_userpwd() -> None:
    items = list(
        ProxyListParser.parse_raw_list_data(
            "invalid-line\nfoo:88\nbar:99:user:pwd",
            proxy_type="socks5",
            proxy_auth=("xuser", "xpwd"),
        )
    )
    assert items[0] == ProxyServer("foo", 88, "xuser", "xpwd", "socks5")
    assert items[1] == ProxyServer("bar", 99, "user", "pwd", "socks5")
