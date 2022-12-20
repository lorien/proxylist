from __future__ import annotations

__all__ = ["ProxyListError", "InvalidProxyLine"]


class ProxyListError(Exception):
    pass


class InvalidProxyLine(ProxyListError):
    pass
