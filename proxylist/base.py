from __future__ import annotations

from abc import abstractmethod

from .server import ProxyServer

__all__ = ["BaseProxySource"]


class BaseProxySource:
    @abstractmethod
    def get_servers_list(self) -> list[ProxyServer]:  # pragma: no cover
        raise NotImplementedError
