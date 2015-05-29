Changelog
=========

The full list of changes between each Python LiveReload release.

Version 2.4.0
-------------

Released on May 29, 2015

1. Fix unicode issue with tornado built-in StaticFileHandler
2. Add filter for directory watching
3. Watch without browser open
4. Auto use inotify wather if possible
5. Add ``open_url_delay`` parameter
6. Refactor lots of code.

Thanks for the patches and issues from everyone.

Version 2.3.2
-------------

Released on Nov 5, 2014

1. Fix root parameter in ``serve`` method via `#76`_.
2. Fix shell unicode stdout error.
3. More useful documentation.

.. _`#76`: https://github.com/lepture/python-livereload/issues/76

Version 2.3.1
-------------

Released on Nov 1, 2014

1. Add ``cwd`` parameter for ``shell``
2. When ``delay`` is ``forever``, it will not trigger a livereload
3. Support different ports for app and livereload.

Version 2.3.0
-------------

Released on Oct 28, 2014

1. Add '--host' argument to CLI
2. Autoreload when python code changed
3. Add delay parameter to watcher


Version 2.2.2
-------------

Released on Sep 10, 2014

Fix for tornado 4.


Version 2.2.1
-------------

Released on Jul 10, 2014

Fix for Python 3.x


Version 2.2.0
-------------

Released on Mar 15, 2014

+ Add bin/livereload
+ Add inotify support

Version 2.1.0
-------------

Released on Jan 26, 2014

Add ForceReloadHandler.

Version 2.0.0
-------------

Released on  Dec 30, 2013

A new designed livereload server which has the power to serve a wsgi
application.

Version 1.0.1
-------------

Release on Aug 19th, 2013

+ Documentation improvement
+ Bugfix for server #29
+ Bugfix for Task #34

Version 1.0.0
-------------

Released on May 9th, 2013

+ Redesign the compiler
+ Various bugfix

Version 0.11
-------------

Released on Nov 7th, 2012

+ Redesign server
+ remove notification


Version 0.8
------------
Released on Jul 10th, 2012

+ Static Server support root page
+ Don't compile at first start

Version 0.7
-------------
Released on Jun 20th, 2012

+ Static Server support index
+ Dynamic watch directory changes

.. _ver0.6:

Version 0.6
------------
Release on Jun 18th, 2012

+ Add static server, 127.0.0.1:35729

.. _ver0.5:

Version 0.5
-----------
Release on Jun 18th, 2012

+ support for python3

.. _ver0.4:

Version 0.4
-----------
Release on May 8th, 2012

+ bugfix for notify (sorry)

.. _ver0.3:

Version 0.3
-----------
Release on May 6th, 2012

+ bugfix for compiler alias
+ raise error for CommandCompiler
+ add comand-line feature
+ get static file from internet

Version 0.2
------------
Release on May 5th, 2012.

+ bugfix
+ performance improvement
+ support for notify-OSD
+ alias of compilers

Version 0.1
------------
Released on May 4th, 2012.
