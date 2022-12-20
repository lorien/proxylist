from __future__ import annotations

import logging
import re
from abc import abstractmethod
from collections.abc import Iterator
from typing import Any, NamedTuple

from .errors import InvalidProxyLine

RE_SIMPLE_PROXY = re.compile(r"^([^:]+):(\d+)$")
RE_AUTH_PROXY = re.compile(r"^([^:]+):(\d+):([^:]+):([^:]+)$")
logger = logging.getLogger(__file__)
__all__ = ["ProxyServer", "BaseProxySource", "InvalidProxyLine"]


class ProxyServer(NamedTuple):
    host: str
    port: int
    username: None | str
    password: None | str
    proxy_type: str

    def get_address(self) -> str:
        return "%s:%s" % (self.host, self.port)

    def get_userpwd(self) -> None | str:
        if self.username:
            return "%s:%s" % (self.username, self.password or "")
        return None


class BaseProxySource:
    def __init__(
        self,
        proxy_type: str = "http",
        proxy_userpwd: None | str = None,
        **kwargs: Any,
    ) -> None:
        kwargs["proxy_type"] = proxy_type
        kwargs["proxy_userpwd"] = proxy_userpwd
        self.config = kwargs

    @abstractmethod
    def load_raw_data(self) -> str:  # pragma: no cover
        raise NotImplementedError

    def parse_proxy_line(self, line: str) -> tuple[str, int, None | str, None | str]:
        """Parse proxy details from the raw text line.

        The text line could be in one of the following formats:
        * host:port
        * host:port:username:password
        """
        line = line.strip()
        match = RE_SIMPLE_PROXY.search(line)
        if match:
            return match.group(1), int(match.group(2)), None, None

        match = RE_AUTH_PROXY.search(line)
        if match:
            host, port, user, pwd = match.groups()
            return host, int(port), user, pwd

        raise InvalidProxyLine("Invalid proxy line: %s" % line)

    def parse_raw_list_data(
        self, data: str, proxy_type: str = "http", proxy_userpwd: None | str = None
    ) -> Iterator[ProxyServer]:
        """Iterate over proxy servers found in the raw data."""
        for orig_line in data.splitlines():
            line = orig_line.strip().replace(" ", "")
            if line and not line.startswith("#"):
                try:
                    host, port, username, password = self.parse_proxy_line(line)
                except InvalidProxyLine as ex:
                    logger.error(ex)
                else:
                    if username is None and proxy_userpwd is not None:
                        username, password = proxy_userpwd.split(":")
                    yield ProxyServer(host, port, username, password, proxy_type)

    def load(self) -> list[ProxyServer]:
        return list(
            self.parse_raw_list_data(
                self.load_raw_data(),
                proxy_type=self.config["proxy_type"],
                proxy_userpwd=self.config["proxy_userpwd"],
            )
        )
