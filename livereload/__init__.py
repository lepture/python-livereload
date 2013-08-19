#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012, Hsiaoming Yang <http://lepture.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of the author nor the names of its contributors
#      may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
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

Install python-livereload
~~~~~~~~~~~~~~~~~~~~~~~~~

Install Python LiveReload with pip::

    $ pip install livereload

If you don't have pip installed, try easy_install::

    $ easy_install livereload


Install Browser Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~

Get Browser Extensions From LiveReload.com

+ Chrome Extension
+ Safari Extension
+ Firefox Extension

Visit: http://help.livereload.com/kb/general-use/browser-extensions

Get Notification
~~~~~~~~~~~~~~~~~

If you are on Mac, and you are a Growl user::

    $ pip install gntp

If you are on Ubuntu, you don't need to do anything. Notification just works.

Working with file protocal
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable file protocal on Chrome:

.. image:: http://i.imgur.com/qGpJI.png


Quickstart
------------

LiveReload is designed for more complex tasks, not just for refreshing a
browser. But you can still do the simple task.

Assume you have livereload and its extension installed, and now you are in your
working directory. With command::

    $ livereload

your browser will reload, if any file in the working directory changed.


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


Others
--------

If you are on a Mac, you can buy `LiveReload2 <http://livereload.com/>`_.

If you are a rubist, you can get guard-livereload.
"""

__version__ = '1.0.1'
__author__ = 'Hsiaoming Yang <me@lepture.com>'
__homepage__ = 'http://lab.lepture.com/livereload/'
