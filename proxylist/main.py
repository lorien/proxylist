from __future__ import annotations

import itertools
import logging
from collections.abc import Iterator, Sequence
from secrets import SystemRandom, choice
from typing import IO, Any, cast
from urllib.error import URLError
from urllib.request import urlopen

from .base import BaseProxySource, ProxyServer

__all__ = ["ProxyList"]
# PROXY_FIELDS = ("host", "port", "username", "password", "proxy_type")
logger = logging.getLogger(__file__)
system_random = SystemRandom()


class FileProxySource(BaseProxySource):
    """Load list from the file."""

    def __init__(self, path: str, **kwargs: Any) -> None:
        self.path = path
        super().__init__(**kwargs)

    def load_raw_data(self) -> str:
        with open(self.path, encoding="utf-8") as inp:
            return inp.read()


class WebProxySource(BaseProxySource):
    """Load list from web resource."""

    def __init__(self, url: str, **kwargs: Any) -> None:
        self.url = url
        super().__init__(**kwargs)

    def load_raw_data(self) -> str:
        limit = 3
        for ntry in range(limit):
            try:
                with urlopen(self.url, timeout=3) as inp:  # nosec B310
                    return cast(IO[bytes], inp).read().decode("utf-8", "ignore")
            except URLError:
                if ntry >= (limit - 1):
                    raise
                logger.debug(
                    "Failed to retrieve proxy list from %s. Retrying.", self.url
                )
        raise Exception("Could not happen")


class ListProxySource(BaseProxySource):
    """Load list from python list of strings."""

    def __init__(self, items: Sequence[str], **kwargs: Any) -> None:
        self.items = items
        super().__init__(**kwargs)

    def load_raw_data(self) -> str:
        return "\n".join(self.items)


class ProxyList:
    """Class to work with proxy list."""

    def __init__(self, source: BaseProxySource) -> None:
        self._source = source
        self._proxy_items: list[ProxyServer] = []
        self._proxy_items_iter: Iterator[ProxyServer] = iter(self._proxy_items)
        self.load()

    @classmethod
    def create_from_file(cls, path: str, **kwargs: Any) -> ProxyList:
        """Create proxy list from file."""
        return ProxyList(FileProxySource(path, **kwargs))

    @classmethod
    def create_from_url(cls, url: str, **kwargs: Any) -> ProxyList:
        """Create proxy list from network document."""
        return ProxyList(WebProxySource(url, **kwargs))

    @classmethod
    def create_from_list(cls, items: Sequence[str], **kwargs: Any) -> ProxyList:
        """Create proxy list from list of strings."""
        return ProxyList(ListProxySource(items, **kwargs))

    def load(self) -> None:
        """Load proxy list from configured proxy source."""
        assert self._source is not None
        self._proxy_items = self._source.load()
        self._proxy_items_iter = itertools.cycle(self._proxy_items)

    def get_random_server(self) -> ProxyServer:
        """Return random server."""
        return choice(self._proxy_items)

    def get_next_server(self) -> ProxyServer:
        """Return next server."""
        # pylint: disable=deprecated-typing-alias
        return next(self._proxy_items_iter)

    def size(self) -> int:
        """Return number of proxies in the list."""
        return len(self._proxy_items)

    def __iter__(self) -> Iterator[ProxyServer]:
        return iter(self._proxy_items)

    def __len__(self) -> int:
        return len(self._proxy_items)

    def __getitem__(self, key: int) -> ProxyServer:
        return self._proxy_items[key]
