LiveReload
==========

This is a brand new LiveReload in version 2.0.0.

Installation
------------

Python LiveReload is designed for web developers who know Python.

Install Python LiveReload with pip::

    $ pip install livereload

If you don't have pip installed, try easy_install::

    $ easy_install livereload


Developer Guide
---------------

The new livereload server is designed for developers. It can power a
wsgi application now::

    from livereload import Server

    server = Server(wsgi_app)
    # run a shell command
    server.watch('static/*.stylus', 'make static')
    # run a function
    server.watch('foo.txt', lambda: print('foo'))
    server.serve()
