from __future__ import annotations

from typing import NamedTuple

__all__ = ["ProxyServer"]


class ProxyServer(NamedTuple):
    host: str
    port: int
    username: None | str
    password: None | str
    proxy_type: None | str

    def get_address(self) -> str:
        return "%s:%s" % (self.host, self.port)

    def get_userpwd(self) -> None | str:
        if self.username:
            return "%s:%s" % (self.username, self.password or "")
        return None
