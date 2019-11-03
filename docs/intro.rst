.. _intro

Introduction
============

This is the documentation for jarpc, a library for asynchronous RPC via `Redis <https://redis.io/>`__ pubsub channels.

It supports 3 runmodes: Client, Server and Slient.

Prerequisites
-------------

jarpc requires a Python version of 3.6 or higher.

Installing
----------

We currently only support installing directly from GitHub: ::

    pip install git+https://github.com/IOMirea/jarpc

You'll also need a working local installation of Redis.

Quick example
-------------

Setup a quick Redis instance via `Docker <https://docker.com/>`__: ::

    docker run --rm --name redis -d -p 6379:6379 redis:5.0.6-alpine


Client example

.. literalinclude:: ../examples/basic/client.py
   :language: python

Server example

.. literalinclude:: ../examples/basic/server.py
    :language: python

Slient example

.. literalinclude:: ../examples/basic/slient.py
    :language: python
