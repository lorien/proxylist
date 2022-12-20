from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Sequence
from http.client import HTTPException
from typing import IO, Any, cast
from urllib.error import URLError
from urllib.request import urlopen

from .base import BaseProxySource
from .errors import ProxySourceReadError
from .parser import parse_servers_from_text
from .server import ProxyServer

logger = logging.getLogger(__file__)
__all__ = ["BaseProxySource"]


class BaseFileProxySource(BaseProxySource):
    def __init__(
        self,
        proxy_type: None | str = None,
        proxy_auth: None | tuple[str, str] = None,
    ) -> None:
        self._default_proxy_type = proxy_type
        self._default_proxy_auth = proxy_auth

    @abstractmethod
    def load_content(self) -> str:  # pragma: no cover
        raise NotImplementedError

    def get_servers_list(self) -> list[ProxyServer]:
        return list(
            parse_servers_from_text(
                self.load_content(),
                proxy_type=self._default_proxy_type,
                proxy_auth=self._default_proxy_auth,
            )
        )


class LocalFileProxySource(BaseFileProxySource):
    """Load list from the file."""

    def __init__(self, path: str, **kwargs: Any) -> None:
        self.path = path
        super().__init__(**kwargs)

    def load_content(self) -> str:
        with open(self.path, encoding="utf-8") as inp:
            return inp.read()


class NetworkFileProxySource(BaseFileProxySource):
    """Load list from web resource."""

    def __init__(self, url: str, **kwargs: Any) -> None:
        self.url = url
        super().__init__(**kwargs)

    def load_content(self) -> str:
        recent_err = None
        for _ in range(3):
            try:
                with urlopen(self.url, timeout=3) as inp:  # nosec B310
                    return cast(IO[bytes], inp).read().decode("utf-8", "ignore")
            except (HTTPException, URLError) as ex:
                recent_err = ex
                logger.debug(
                    "Failed to retrieve proxy list from %s. Retrying.", self.url
                )
        raise ProxySourceReadError(
            "Could not load data from {}".format(self.url)
        ) from recent_err


class LinesListProxySource(BaseFileProxySource):
    """Load list from python list of strings."""

    def __init__(self, lines: Sequence[str], **kwargs: Any) -> None:
        self._lines = lines
        super().__init__(**kwargs)

    def load_content(self) -> str:
        return "\n".join(self._lines)
