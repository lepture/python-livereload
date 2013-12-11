.. _quickstart:

Quickstart
==========

This section assumes that you have everything installed. If you do not,
head over to the :ref:`installation` section.

Commandline Guide
-----------------


Program Guide
-------------

A simple example::

    from livereload import Server, Task
    from livereload.compiler import shell

    Task.add('public/*.styl', shell('make static'))
    Server(wsgi_app, port=8000).serve()
