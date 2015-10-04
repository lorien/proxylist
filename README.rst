=========
proxylist
=========

.. image:: https://travis-ci.org/lorien/proxylist.png?branch=master
    :target: https://travis-ci.org/lorien/proxylist?branch=master

.. image:: https://img.shields.io/pypi/dm/proxylist.svg
    :target: https://pypi.python.org/pypi/proxylist

.. image:: https://img.shields.io/pypi/v/proxylist.svg
    :target: https://pypi.python.org/pypi/proxylist

.. image:: https://readthedocs.org/projects/proxylist/badge/?version=latest
    :target: http://user-agent.readthedocs.org


What is proxylist library?
--------------------------

The proxylist lib is for loading list of proxy servers and rotate/select
them in you network client. Proxylist supports loading data from:

* local file
* network resource
* python list of dicts 


Usage Example
-------------

.. code:: python

    >>> from proxylist import ProxyList
    >>> pl = ProxyList()
    >>> pl.load_file('/web/proxy.txt')
    >>> pl.random()
    <proxylist.base.Proxy object at 0x7f1882d599e8>
    >>> pl.random().address()
    '1.1.1.1:8085'
    >>> len(pl)
    1000



Installation
------------

Use pip:

.. code:: shell

    $ pip install -U proxylist


.. Documentation
.. -------------

.. Documentation is available at http://proxylist.readthedocs.org



Contribution
============

Use github to submit bug,fix or wish request: https://github.com/lorien/proxylist/issues
