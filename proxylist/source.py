from __future__ import annotations

import logging
import re
from abc import abstractmethod
from collections.abc import Iterator, Sequence
from typing import IO, Any, cast
from urllib.error import URLError
from urllib.request import urlopen

from .errors import InvalidProxyLine
from .server import ProxyServer

RE_SIMPLE_PROXY = re.compile(r"^([^:]+):(\d+)$")
RE_AUTH_PROXY = re.compile(r"^([^:]+):(\d+):([^:]+):([^:]+)$")
logger = logging.getLogger(__file__)
__all__ = ["BaseProxySource"]


class BaseProxySource:
    def __init__(
        self,
        proxy_type: None | str = None,
        proxy_auth: None | tuple[str, str] = None,
    ) -> None:
        self._default_proxy_type = proxy_type
        self._default_proxy_auth = proxy_auth

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
        self,
        data: str,
        proxy_type: None | str,
        proxy_auth: None | tuple[str, str] = None,
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
                    if username is None and proxy_auth:
                        username, password = proxy_auth
                    yield ProxyServer(host, port, username, password, proxy_type)

    def load(self) -> list[ProxyServer]:
        return list(
            self.parse_raw_list_data(
                self.load_raw_data(),
                proxy_type=self._default_proxy_type,
                proxy_auth=self._default_proxy_auth,
            )
        )


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
