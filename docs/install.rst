.. _installation:

Installation
=============

This section covers the installation of Python LiveReload and other
essentials to make LiveReload available.

LiveReload contains two parts, the client side and the server side.
Client means the browser, it listens to the server's signal, and refreshs
your browser when catching the proper signals.

Install Browser Extensions
----------------------------

A browser extension is not required, you can insert a script into your
html page manually::

    <script type="text/javascript" src="http://127.0.0.1:35729/livereload.js"></script>

But a browser extension will make your life easier, available extensions:

+ Chrome Extension
+ Safari Extension
+ Firefox Extension

Visit: http://help.livereload.com/kb/general-use/browser-extensions


Distribute & Pip
-----------------

Installing Python LiveReload is simple with pip::

    $ pip install livereload

If you don't have pip installed, try easy_install::

    $ easy_install livereload


Enhancement
------------

Python LiveReload is designed to do some complex tasks like compiling.
The package itself has provided some useful compilers for you. But
you need to install them first.

Get Lesscss
~~~~~~~~~~~~

Lesscss_ is a dynamic stylesheet language that makes css more elegent.

Install less with npm::

    $ npm install less -g

Get UglifyJS
~~~~~~~~~~~~

UglifyJS_ is a popular JavaScript parser/compressor/beautifier.

Install UglifyJS with npm::

    $ npm install uglify-js -g


Get slimmer
~~~~~~~~~~~~

Slimmer is a python library that compressing css, JavaScript, and
html.

Install slimmer::

    $ pip install slimmer

.. _Lesscss: http://lesscss.org
.. _UglifyJs: https://github.com/mishoo/UglifyJS
