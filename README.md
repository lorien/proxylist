# Proxylist Package

[![Test Status](https://github.com/lorien/proxylist/actions/workflows/test.yml/badge.svg)](https://github.com/lorien/proxylist/actions/workflows/test.yml)
[![Code Quality](https://github.com/lorien/proxylist/actions/workflows/check.yml/badge.svg)](https://github.com/lorien/proxylist/actions/workflows/test.yml)
[![Type Check](https://github.com/lorien/proxylist/actions/workflows/mypy.yml/badge.svg)](https://github.com/lorien/proxylist/actions/workflows/mypy.yml)
[![Test Coverage Status](https://coveralls.io/repos/github/lorien/proxylist/badge.svg)](https://coveralls.io/github/lorien/proxylist)
[![Pypi Downloads](https://img.shields.io/pypi/dw/proxylist?label=Downloads)](https://pypistats.org/packages/proxylist)
[![Documentation Status](https://readthedocs.org/projects/proxylist/badge/?version=latest)](http://user-agent.readthedocs.org)

The proxylist package provides function and classes for:

- loading list of proxy servers from different sources like local file or network location
- rotating proxy servers or picking them randomly


## Usage Example

```
>>> from proxylist import ProxyList
>>> pl = ProxyList.create_from_file('var/proxy.txt')
>>> pl.get_random_server()
<proxylist.server.ProxyServer object at 0x7f1882d599e8>
>>> pl.get_random_server().address()
'1.1.1.1:8085'
>>> len(pl)
1000
```

## Installation

Run: `pip install -U proxylist`


## Documentation

Documentation is available at http://proxylist.readthedocs.org



## Community

Telegram English chat: [https://t.me/grablab](https://t.me/grablab)

Telegram Russian chat: [https://t.me/grablab\_ru](https://t.me/grablab_ru)
