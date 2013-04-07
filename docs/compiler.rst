.. _compiler:


Compiler
=========

In web development, compiling (compressing) is a common task, Python LiveReload
has provided some compilers for you.


Overview
----------

In :ref:`quickstart` and :ref:`guardfile` you already know ``lessc``. It is simple.
But ``lessc`` just write code to a file, sometimes you don't want to write
code, you want to append code. In this case, you should know the basic of a
`Compiler`.

``CommandCompiler`` takes source path for constructor,
and has ``init_command()`` method to setup a executable.

::

    from livereload.compiler import CommandCompiler

    c = CommandCompiler('style.less')
    c.init_command('lessc --compress')
    c.write('site.css')  #: write compiled code to 'site.css'
    c.append('global.css')  #: append compiled code to 'global.css'


Quick Alias
------------

In most cases, you don't need to write every `Compiler`, you can use a simple
and easy alias. The available:

+ lessc
+ uglifyjs
+ slimmer
+ coffee
+ shell

These aliases accept ``mode`` parameter to switch calling ``write()`` or ``append()``.
"``w``" leads ``write()``, while "``a``" leads ``append()``. And "``w``" is the default value.

Above example can be changed as followings::

    from livereload.compiler import lessc

    lessc('style.less', 'site.css')
    lessc('style.less', 'global.css', mode='a')

Get static files from internet
-------------------------------

New in :ref:`ver0.3`.

With this new feature, you can keep the source of your project clean.
If the path starts with "``http://``" or "``https://``", download it automatically. ::

    from livereload.compiler import uglifyjs

    uglifyjs('http://code.jquery.com/jquery.js', 'static/lib.js')


Invoke command line task
------------------------

Using ``shell``, you can invoke any command line tasks such as *Sphinx*
html documentation::

    from livereload.task import Task
    from livereload.compiler import shell

    Task.add('*.rst', shell('make html'))


Contribute
-----------

Want more compiler?

Fork GitHub Repo and send pull request to me.
