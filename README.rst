LiveReload
==========

Reload webpages on changes, without hitting refresh in your browser.

Installation
------------

python-livereload is for web developers who know Python, and is available on
`PyPI <https://pypi.python.org/pypi/livereload>`_.

::

    $ pip install livereload

Command Line Interface
----------------------

python-livereload provides a command line utility, ``livereload``, for starting a server in a directory.

By default, it will listen to port 35729, the common port for `LiveReload browser extensions`_. ::

    $ livereload --help
    usage: livereload [-h] [-p PORT] [-w WAIT] [directory]

    Start a `livereload` server

    positional arguments:
      directory             Directory to watch for changes

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Port to run `livereload` server on
      -w WAIT, --wait WAIT  Time delay before reloading

.. _`livereload browser extensions`: http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-

Older versions of python-livereload used a ``Guardfile`` to describe optional additional rules for files to watch and build commands to run on changes.  This conflicted with other tools that used the same file for their configuration and is no longer supported since python-livereload 2.0.0.  Instead of a ``Guardfile`` you can now write a Python script using very similar syntax and run it instead of the command line application.

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

server.setHeader
~~~~~~~~~~~~~~~~

```server.setHeader``` can be used to add one or more headers to the HTTP 
response::

    server.setHeader('Access-Control-Allow-Origin', '*')
    server.setHeader('Access-Control-Allow-Methods', '*')


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

    # open the web browser on startup, based on $BROWSER environment variable
    server.serve(open_url_delay=5, debug=False)

    # set a custom default file to open
    server.serve(default_filename='example.html')


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

For Django there is a management command included.

To use simply

- add ``'livereload'`` to your ``INSTALLED_APPS`` and
- then run ``./manage.py livereload``.

For available options like host and ports please refer to ``./manage.py livereload -h``.

To automagically serve static files like the native ``runserver`` command you have to use `dj-static <https://github.com/kennethreitz/dj-static>`_. (follow the simple instructions there).

Flask
~~~~~

Wrap Flask with livereload is much simpler:

.. code:: python

    # app is a Flask object
    app = create_app()

    # remember to use DEBUG mode for templates auto reload
    # https://github.com/lepture/python-livereload/issues/144
    app.debug = True

    server = Server(app.wsgi_app)
    # server.watch
    server.serve()


Bottle
~~~~~~

Wrap the ``Bottle`` app with livereload server:

.. code:: python

    # Without this line templates won't auto reload because of caching.
    # http://bottlepy.org/docs/dev/tutorial.html#templates
    bottle.debug(True)

    app = Bottle()
    server = Server(app)
    # server.watch
    server.serve()


pyinotify
---------

If `pyinotify <https://pypi.org/project/pyinotify/>`_ is installed, it will be used for watching file changes instead of the built in polling based watcher. If you prefer to use the built in watcher, specify the ``--poll`` flag on the command line, or initialize the ``Server`` class in a script like in the following

.. code:: python
	  
   from livereload import Server
   from livereload.watcher import Watcher
   
   server = Server(watcher=Watcher())

The `pyinotify <https://pypi.org/project/pyinotify/>`_ watcher is more efficient than the built in polling based watcher since it does not have to continously poll, but it might fail if the inode of the watched file changes, as might happen when doing a move or a copy or using certain editors such as vi or emacs with backup settings enabled.
 
Security Report
---------------

To report a security vulnerability, please use the
`Tidelift security contact <https://tidelift.com/security>`_.
Tidelift will coordinate the fix and disclosure.
