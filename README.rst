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

Older versions of Python LiveReload used a ``Guardfile`` to describe optional additional rules for files to watch and build commands to run on changes.  This conflicted with other tools that used the same file for their configuration and is no longer supported since Python LiveReload version 2.0.0.  Instead of a ``Guardfile`` you can now write a Python script using very similar syntax and run it instead of the command line application.

Script example: Sphinx
----------------------

Here's a simple example script that rebuilds Sphinx documentation:

.. code:: python

    #!/usr/bin/env python
    from livereload import Server, shell
    server = Server()
    server.watch('docs/*.rst', shell('make html', cwd='docs'))
    server.serve(root='docs/_build/html')

Run it, then open http://localhost:5500/ and you can see the documentation changes in real time.

Developer Guide
---------------

The new livereload server is designed for developers. It can power a
wsgi application now:

.. code:: python

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

    # open the web browser on startup
    server.serve(open_url=True, debug=False)


shell
~~~~~

The powerful ``shell`` function will help you to execute shell commands. You
can use it with ``server.watch``::

    # you can redirect command output to a file
    server.watch('style.less', shell('lessc style.less', output='style.css'))

    # commands can be a list
    server.watch('style.less', shell(['lessc', 'style.less'], output='style.css'))

    # working with Makefile
    server.watch('assets/*.styl', shell('make assets', cwd='assets'))


Frameworks Integration
----------------------

Livereload can work seamlessly with your favorite framework.

Django
~~~~~~

Here is a little hint on Django. Change your ``manage.py`` file to:

.. code:: python

    #!/usr/bin/env python
    import os
    import sys

    if __name__ == "__main__":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hello.settings")

        from django.core.management import execute_from_command_line

        if 'livereload' in sys.argv:
            from django.core.wsgi import get_wsgi_application
            from livereload import Server
            application = get_wsgi_application()
            server = Server(application)

            # Add your watch
            # server.watch('path/to/file', 'your command')
            server.serve()
        else:
            execute_from_command_line(sys.argv)

When you execute ``./manage.py livereload``, it will start a livereload server.


Flask
~~~~~

Wrap Flask with livereload is much simpler:

.. code:: python

    # app is a Flask object
    app = create_app()

    server = Server(app.wsgi_app)
    # server.watch
    server.serve()


Bottle
~~~~~~

Wrap the ``Bottle`` app with livereload server:

.. code:: python

    app = Bottle()
    server = Server(app)
    # server.watch
    server.serve()
