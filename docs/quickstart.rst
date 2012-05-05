.. _quickstart:

Quickstart
==========

This section assumes that you have everything installed. If you do not,
head over to the :ref:`installation` section.


Simple Task
------------

LiveReload is designed for more complex tasks, not just for refreshing a
browser. But you can still do the simple task.

Assume you have livereload and its extension installed, and now you are in your
working directory. With command::

    $ livereload

your browser will reload, if any file in the working directory changed.


Working with file protocal
---------------------------

Enable file protocal on Chrome:

.. image:: http://i.imgur.com/qGpJI.png


Guardfile
----------
More complex tasks can be done by Guardfile. Write a Guardfile in your working
directory, the basic syntax::

    #!/usr/bin/env python
    from livereload.task import Task

    Task.add('static/style.css')
    Task.add('*.html')

Now livereload will only guard static/style.css and html in your workding
directory.

But python-livereload is more than that, you can specify a task before
refreshing the browser::

    #!/usr/bin/env python
    from livereload.task import Task
    from livereload.compiler import lessc

    Task.add('style.less', lessc('style.less', 'style.css'))

And it will compile less css before refreshing the browser now.

Want to know about :ref:`guardfile` ?


Commands like Makefile
-----------------------

New in :ref:`ver0.3`

If you want to do some tasks in Guardfile manually::

    # Guardfile

    def task1():
        print('task1')

    def task2():
        print('task2')

In terminal::

    $ livereload task1 task2


Others
--------

If you are on a Mac, you can buy `LiveReload2 <http://livereload.com/>`_.

If you are a rubist, you can get guard-livereload.
