from __future__ import annotations

import logging
import re
from collections.abc import Iterator

from .errors import InvalidProxyLine
from .server import ProxyServer

__all__ = ["parse_proxy_line", "parse_servers_from_text"]

RE_SIMPLE_PROXY = re.compile(r"^([^:]+):(\d+)$")
RE_AUTH_PROXY = re.compile(r"^([^:]+):(\d+):([^:]+):([^:]+)$")
logger = logging.getLogger(__file__)


def parse_proxy_line(line: str) -> tuple[str, int, None | str, None | str]:
    """Parse proxy details from the text line.

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


def parse_servers_from_text(
    data: str,
    proxy_type: None | str,
    proxy_auth: None | tuple[str, str] = None,
) -> Iterator[ProxyServer]:
    """Iterate proxy servers found in the content of text file."""
    for orig_line in data.splitlines():
        line = orig_line.strip()
        if line and not line.startswith("#"):
            try:
                host, port, username, password = parse_proxy_line(line)
            except InvalidProxyLine as ex:
                logger.error(ex)
            else:
                if username is None and proxy_auth:
                    username, password = proxy_auth
                yield ProxyServer(host, port, username, password, proxy_type)
