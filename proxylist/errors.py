from __future__ import annotations

__all__ = ["ProxyListError", "InvalidProxyLine", "ProxySourceReadError"]


class ProxyListError(Exception):
    pass


class InvalidProxyLine(ProxyListError):
    pass


class ProxySourceReadError(ProxyListError):
    pass
