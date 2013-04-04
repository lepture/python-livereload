.. _guardfile:

Guardfile
=========

:file:`Guardfile` is an executable python file which defines the tasks Python LiveReload
should guard.

Writing Guardfile is simple (or not).

The basic syntax::

    #!/usr/bin/env python
    from livereload.task import Task

    Task.add('static/style.css')

Which means our Server should guard ``static/style.css`` , when this (and only this)
file is saved, the server will send a signal to the client side, and the browser
will refresh itself.


Add a task
-----------

In Guardfile, the most important thing is adding a task::

    Task.add(...)

``Task.add`` accepts two parameters:

1. the first one is the path you want to guard
2. the second one is optional, it should be a callable function


Define a path
--------------

Path is the first parameter of a Task, a path can be absolute or relative:

1. a filepath: ``static/style.css``
2. a directory path: ``static``
3. a glob pattern: ``static/*.css``


Define a function
-------------------

Function is the second parameter of a Task, it is not required.
When files in the given path changed, the related function will execute.

A good example in :ref:`quickstart`::

    #!/usr/bin/env python
    from livereload.task import Task
    from livereload.compiler import lessc

    Task.add('style.less', lessc('style.less', 'style.css'))

This means when ``style.less`` is saved, the server will execute::

    lessc('style.less', 'style.css')()

Please note that ``lessc`` here will create a function. You can't do::

    #!/usr/bin/env python
    from livereload.task import Task

    def say(word):
        print(word)

    Task.add('style.less', say('hello'))

Because ``say('hello')`` is not a callable function, it is executed already.
But you can easily create a function by::

    #!/usr/bin/env python
    from livereload.task import Task
    import functools

    @functools.partial
    def say(word):
        print(word)

    Task.add('style.less', say('hello'))

And there is one more thing you should know. When the function is called,
it losts its context already, which means you should never import a module
outside of the task function::

    #: don't
    import A

    def task1():
        return A.do_some_thing()

    #: do
    def task2():
        import B
        return B.do_some_thing()


Python LiveReload provides some common tasks for web developers,
check :ref:`compiler` .
