from proxylist.base import ProxyServer


def test_get_address() -> None:
    assert ProxyServer("foo", 88, None, None, "socks5").get_address() == "foo:88"


def test_get_userpwd_not_set() -> None:
    assert ProxyServer("foo", 88, None, None, "socks5").get_userpwd() is None


def test_get_userpwd() -> None:
    assert ProxyServer("foo", 88, "user", "pwd", "socks5").get_userpwd() == "user:pwd"


def test_get_userpwd_username_none() -> None:
    assert ProxyServer("foo", 88, None, "pwd", "socks5").get_userpwd() is None


def test_get_userpwd_password_none() -> None:
    assert ProxyServer("foo", 88, "user", None, "socks5").get_userpwd() == "user:"
