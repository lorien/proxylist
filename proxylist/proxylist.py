from __future__ import annotations

import itertools
import logging
from collections.abc import Iterator, Sequence
from secrets import choice
from typing import Any

from .server import ProxyServer
from .source import (
    BaseProxySource,
    LinesListProxySource,
    LocalFileProxySource,
    NetworkFileProxySource,
)

__all__ = ["ProxyList"]
logger = logging.getLogger(__file__)


class ProxyList:
    """Class to work with proxy list."""

    def __init__(self, source: BaseProxySource) -> None:
        self._source = source
        self._servers_list: list[ProxyServer] = []
        self._servers_list_iter: Iterator[ProxyServer] = iter(self._servers_list)
        self.load()

    @classmethod
    def from_local_file(cls, path: str, **kwargs: Any) -> ProxyList:
        """Create proxy list from file."""
        return ProxyList(LocalFileProxySource(path, **kwargs))

    @classmethod
    def from_network_file(cls, url: str, **kwargs: Any) -> ProxyList:
        """Create proxy list from network document."""
        return ProxyList(NetworkFileProxySource(url, **kwargs))

    @classmethod
    def from_lines_list(cls, items: Sequence[str], **kwargs: Any) -> ProxyList:
        """Create proxy list from list of strings."""
        return ProxyList(LinesListProxySource(items, **kwargs))

    def load(self) -> None:
        """Load proxy list from configured proxy source."""
        assert self._source is not None
        self._servers_list = self._source.get_servers_list()
        self._servers_list_iter = itertools.cycle(self._servers_list)

    def get_random_server(self) -> ProxyServer:
        """Return random server."""
        return choice(self._servers_list)

    def get_next_server(self) -> ProxyServer:
        """Return next server."""
        return next(self._servers_list_iter)

    def size(self) -> int:
        """Return number of proxies in the list."""
        return len(self._servers_list)

    def __iter__(self) -> Iterator[ProxyServer]:
        return iter(self._servers_list)

    def __len__(self) -> int:
        return len(self._servers_list)

    def __getitem__(self, key: int) -> ProxyServer:
        return self._servers_list[key]
