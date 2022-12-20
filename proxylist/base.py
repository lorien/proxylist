from __future__ import annotations

from collections.abc import Iterator

from .server import ProxyServer

__all__ = ["BaseProxyListParser"]


class BaseProxyListParser:
    @classmethod
    def parse_proxy_line(
        cls, line: str
    ) -> tuple[str, int, None | str, None | str]:  # pragma: no cover
        raise NotImplementedError

    @classmethod
    def parse_raw_list_data(
        cls,
        data: str,
        proxy_type: None | str,
        proxy_auth: None | tuple[str, str] = None,
    ) -> Iterator[ProxyServer]:  # pragma: no cover
        raise NotImplementedError
