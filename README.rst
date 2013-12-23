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
- watcher: a watcher instance, you don't have to create one

server.watch
~~~~~~~~~~~~

``server.watch`` can watch a filepath, a directory and a glob pattern::

    server.watch('path/to/file.txt')
    server.watch('directory/path/')
    server.watch('glob/*.pattern')

You can also use other library (for example: formic) for more powerful
file adding::

    for filepath in formic.FileSet(include="**.css"):
        server.watch(filepath, 'make css')
