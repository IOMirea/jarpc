.. _intro

Introduction
============

This is the documentation for yarpc, a library for asynchronous RPC via `Redis <https://redis.io/>`__ pubsub channels.

It supports 2 runmodes: Client and Server. Support for ClientServer is planned.

Prerequisites
-------------

yarpc requires a Python version of 3.7 or higher.

Installing
----------

We currently only support installing directly from GitHub: ::

    pip install git+https://github.com/IOMirea/yarpc

You'll also need a working local installation of Redis.

Quick example
-------------

Setup a quick Redis instance via `Docker <https://docker.com/>`__: ::

    docker run --rm --name redis -d -p 6379:6379 redis:5.0.6-alpine


Client example

.. literalinclude:: ../examples/client.py
   :language: python

Server example

.. literalinclude:: ../examples/server.py
    :language: python
