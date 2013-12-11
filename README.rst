Python LiveReload
=================

`LiveReload  <http://livereload.com/>`_ Server in Python Version.

Web Developers need to refresh a browser everytime when he saved a file (css,
javascript, html), it is really boring. LiveReload will take care of that for
you. When you saved a file, your browser will refresh itself. And what's more,
it can do some tasks like compiling less to css before the browser refreshing.

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

    from livereload import Server, Task
    from livereload.compiler import shell

    Task.add('public/*.less', shell('make static'))
    Server(wsgi_app, port=8000).serve()
