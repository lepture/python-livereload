.. _compiler:


Compiler
=========

In web development, compiling(compressing) is a common task, Python LiveReload
has provided some compilers for you.


Overview
----------

In :ref:`quickstart` and :ref:`guardfile` you already know ``lessc``. It is simple.
But ``lessc`` just write code to a file, sometimes you don't want to write
code, you want to append code. In this case, you should know the basic of a
Compiler.

Take LessCompiler as the example::

    from livereload.compiler import LessCompiler

    #: init
    less = LessCompiler('style.less')

    #: write
    less.write('site.css')

    #: append
    less.append('global.css')


All Compilers have the same API, available compilers:

+ LessCompiler
+ UglifyJSCompiler
+ SlimmerCompiler


Quick Alias
------------

In most cases, you don't need to write every Compiler, you need a simple
and easy alias. The available:

+ lessc
+ uglifyjs
+ slimmer


Get static files from internet
-------------------------------

New in :ref:`ver0.3`.

With this new feature, you can keep the source of your project clean::

    js = UglifyJSCompiler('http://code.jquery.com/jquery.js')
    js.write('static/lib.js')


Contribute
-----------

Want more compiler?

Fork GitHub Repo and send pull request to me.
