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

    from livereload import Server, shell

    server = Server(wsgi_app)

    # run a shell command
    server.watch('static/*.stylus', 'make static')

    # run a function
    def alert():
        print('foo')
    server.watch('foo.txt', alert)

    # output stdout into a file
    server.watch('style.less', shell('lessc style.less', output='style.css'))

    server.serve()

The ``Server`` class accepts parameters:

- app: a wsgi application
- port: server port, default is 5500
- root: if **app** is not specified, it will serve a static server at this give root
- watcher: a watcher instance, you don't have to create one
