LiveReload
==========

This is a brand new LiveReload in version 2.0.0.

.. image:: https://pypip.in/d/livereload/badge.png
   :target: https://pypi.python.org/pypi/livereload
   :alt: Downloads
.. image:: https://pypip.in/v/livereload/badge.png
   :target: https://pypi.python.org/pypi/livereload
   :alt: Version


Installation
------------

Python LiveReload is designed for web developers who know Python.

Install Python LiveReload with pip::

    $ pip install livereload

If you don't have pip installed, try easy_install::

    $ easy_install livereload

Command Line Interface
----------------------

Python LiveReload provides a command line utility, ``livereload``, for starting a server in a directory.

By default, it will listen to port 35729, the common port for `LiveReload browser extensions`_. ::

    $ livereload --help
    usage: livereload [-h] [-p PORT] [directory]

    Start a `livereload` server

    positional arguments:
      directory             Directory to watch for changes

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Port to run `livereload` server on

.. _`livereload browser extensions`: http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-

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

You can delay a certain seconds to send the reload signal::

    # delay 2 seconds for reloading
    server.watch('path/to/file', delay=2)


server.serve
~~~~~~~~~~~~

Setup a server with ``server.serve`` method. It can create a static server
and a livereload server::

    # use default settings
    server.serve()

    # livereload on another port
    server.serve(liveport=35729)

    # use custom host and port
    server.serve(port=8080, host='localhost')


shell
~~~~~

The powerful ``shell`` function will help you to execute shell commands. You
can use it with ``server.watch``::

    server.watch('style.less', shell('lessc style.less', output='style.css'))

    # commands can be a list
    server.watch('style.less', shell(['lessc', 'style.less'], output='style.css'))

    # working with Makefile
    server.watch('assets/*.styl', shell('make assets', cwd='assets'))
