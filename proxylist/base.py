"""
Module to load proxy list and select/rotate proxies from it.
"""
from __future__ import absolute_import
import re
import itertools
import logging
from random import randint
import six
from six.moves.urllib.request import urlopen

__all__ = ('Proxy', 'InvalidProxyLine', 'FileProxySource',
           'WebProxySource', 'ListProxySource', 'ProxyList')
RE_SIMPLE_PROXY = re.compile(r'^([^:]+):([^:]+)$')
RE_AUTH_PROXY = re.compile(r'^([^:]+):([^:]+):([^:]+):([^:]+)$')
PROXY_STANDARD_ATTRS = ('host', 'port', 'username', 'password')
logger = logging.getLogger('proxylist')

class Proxy(object):
    __slots__ = ('host', 'port', 'username', 'password',
                 'proxy_type', 'meta')

    def __init__(self, host=None, port=None, username=None,
                 password=None, proxy_type=None, meta=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.proxy_type = proxy_type
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

    def __str__(self):
        return '<Proxy %s:%s>' % (self.host, self.port)

    def address(self):
        return '%s:%s' % (self.host, self.port)

    def get_address(self):
        # TODO: deprecation warning
        return self.address

    def userpwd(self):
        if self.username:
            return '%s:%s' % (self.username, self.password or '')
        else:
            return None



class ProxyListError(Exception):
    pass


class InvalidProxyLine(ProxyListError):
    pass


class NotEnoughData(ProxyListError):
    pass


def parse_proxy_line(line):
    """
    Parse proxy details from the raw text line.

    The text line could be in one of the following formats:
    * host:port
    * host:port:username:password
    """

    line = line.strip()
    match = RE_SIMPLE_PROXY.search(line)
    if match:
        return match.group(1), match.group(2), None, None

    match = RE_AUTH_PROXY.search(line)
    if match:
        host, port, user, pwd = match.groups()
        return host, port, user, pwd

    raise InvalidProxyLine('Invalid proxy line: %s' % line)


def parse_raw_list_data(data, proxy_type='http', proxy_userpwd=None,
                        item_format=None):
    "Iterate over proxy servers found in the raw data"
    if not isinstance(data, six.text_type):
        data = data.decode('utf-8')
    if item_format is None:
        rex_format = None
    else:
        strict_item_format = '^%s$' % item_format.lstrip('^').rstrip('$')
        rex_format = re.compile(strict_item_format, re.I)

    for orig_line in data.splitlines():
        line = orig_line.strip()
        # If not format is defined then try few common
        # format to extract proxy data from each item in the list
        if rex_format is None:
            line = line.replace(' ', '')
            if line and not line.startswith('#'):
                try:
                    host, port, username, password = parse_proxy_line(line)
                except InvalidProxyLine as ex:
                    logger.error(ex)
                    continue
                else:
                    proxy = Proxy(host, port, username, password, proxy_type)
            else:
                continue
        else:
            match = rex_format.match(line)
            if match is None:
                ex = InvalidProxyLine('Proxy line %s does not match format %s'
                                      % (line, item_format))
                logger.error(ex)
                continue
            data = match.groupdict()
            meta = dict((x, y) for x, y in data.items()
                        if x not in PROXY_STANDARD_ATTRS)
            proxy = Proxy(data['host'], data['port'],
                          data.get('username'), data.get('password'),
                          proxy_type=proxy_type, meta=meta)
            for key in ('host', 'port', 'username', 'password', 'proxy_type'):
                if key in data:
                    del data[key]
        if proxy.username is None and proxy_userpwd is not None:
            username, password = proxy_userpwd.split(':')
            proxy.username = username
            proxy.password = password
        yield proxy




class BaseProxySource(object):
    def __init__(self, proxy_type='http', proxy_userpwd=None,
                 item_format=None, **kwargs):
        self.proxy_type = proxy_type
        self.item_format = item_format
        self.proxy_userpwd = proxy_userpwd

    def load_raw_data(self):
        raise NotImplementedError

    def load(self):
        data = self.load_raw_data()
        return list(parse_raw_list_data(
            data,
            proxy_type=self.proxy_type,
            proxy_userpwd=self.proxy_userpwd,
            item_format=self.item_format,
        ))


class FileProxySource(BaseProxySource):
    "Proxy source that loads list from the file"
    def __init__(self, path, **kwargs):
        self.path = path
        super(FileProxySource, self).__init__(**kwargs)

    def load_raw_data(self):
        with open(self.path) as inp:
            return inp.read()


class WebProxySource(BaseProxySource):
    "Proxy source that loads list from web resource"
    def __init__(self, url, timeout=5, try_count=3, **kwargs):
        self.url = url
        self.timeout = timeout
        self.try_count = try_count
        super(WebProxySource, self).__init__(**kwargs)

    def load_raw_data(self):
        for count in range(self.try_count):
            try:
                data = urlopen(url=self.url, timeout=self.timeout).read()
            except Exception as ex: # TODO: more specific exceptions
                if count >= (self.try_count - 1):
                    raise
            else:
                return data.decode('utf-8')


class ListProxySource(BaseProxySource):
    """That proxy source that loads list from
    python list of strings"""
    def __init__(self, items, **kwargs):
        self.items = items
        super(ListProxySource, self).__init__(**kwargs)

    def load_raw_data(self):
        return '\n'.join(self.items)


class ProxyList(object):
    """
    Class to work with proxy list.
    """

    def __init__(self, source=None):
        self._source = source
        self._list = []
        self._list_iter = None

    def set_source(self, source):
        "Set the proxy source and use it to load proxy list"
        self._source = source
        self.load()

    def load_file(self, path, **kwargs):
        "Load proxy list from file"
        self.set_source(FileProxySource(path, **kwargs))

    def load_url(self, url, **kwargs):
        "Load proxy list from web document"
        self.set_source(WebProxySource(url, **kwargs))

    def load_list(self, items, **kwargs):
        "Load proxy list from python list"
        self.set_source(ListProxySource(items, **kwargs))

    def load(self):
        "Load proxy list from configured proxy source"
        self._list = self._source.load()
        self._list_iter = itertools.cycle(self._list)

    def random(self):
        "Return random proxy"
        idx = randint(0, len(self._list) - 1)
        return self._list[idx]

    def next(self):
        "Return next proxy"
        return next(self._list_iter)

    def size(self):
        "Return number of proxies in the list"
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]

    # Deprecated stuff

    def get_next_proxy(self):
        "Return next proxy"
        # TODO: deprecation warning
        return self.next()

    def get_random_proxy(self):
        "Return random proxy"
        # TODO: deprecation warning
        return self.random()
