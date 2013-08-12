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

A browser extension is not required, you can insert a script into your
html page manually::

    <script type="text/javascript" src="http://127.0.0.1:35729/livereload.js"></script>

But a browser extension will make your life easier, available extensions:

+ Chrome Extension
+ Safari Extension
+ Firefox Extension

Visit: http://help.livereload.com/kb/general-use/browser-extensions

Quickstart
------------

LiveReload is designed for more complex tasks, not just for refreshing a
browser. But you can still do the simple task.

Assume you have livereload and its extension installed, and now you are in your
working directory. With command::

    $ livereload [-p port]

your browser will reload, if any file in the working directory changed.


LiveReload as SimpleHTTPServer
-------------------------------

Livereload server can be a SimpleHTTPServer::

    $ livereload -p 8000

It will set up a server at port 8000, take a look at http://127.0.0.1:8000.
Oh, it can livereload!

**IF YOU ARE NOT USING IT AS A HTTP SERVER, DO NOT ADD THE PORT OPTION**.

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


Linux
----------

If you're using python-livereload under Linux, you should also install pyinotify,
as it will greatly improve responsiveness and reduce CPU load.

You may see errors such as::

    [2013-06-19 11:11:07,499 pyinotify ERROR] add_watch: cannot watch somefile WD=-1, Errno=No space left on device (ENOSPC)

If so, you need to increase the number of "user watches". You can either do this temporarily by running (as root)::

    echo 51200 > /proc/sys/fs/inotify/max_user_watches

To make this change permanent, add the following line to /etc/sysctl.conf and reboot::

    fs.inotify.max_user_watches = 51200


Others
--------

If you are on a Mac, you can buy `LiveReload2 <http://livereload.com/>`_.

If you are a rubist, you can get guard-livereload.
