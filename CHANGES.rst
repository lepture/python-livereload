Changelog
=========

The full list of changes between each Python LiveReload release.

Version 2.6.3
-------------

Released on August 22, 2020

1. Support for custom default filenames.


Version 2.6.2
-------------

Released on June 6, 2020

1. Support for Python 2.8
2. Enable adding custom headers to response.
3. Updates for Python 2.7 support.
4. Support for use with a reverse proxy.
5. Other bug fixes.


Version 2.6.1
-------------

Released on May 7, 2019

1. Fixed bugs

Version 2.6.0
-------------

Released on Nov 21, 2018

1. Changed logic of liveport.
2. Fixed bugs

Version 2.5.2
-------------

Released on May 2, 2018

1. Fix tornado 4.5+ not closing connection
2. Add ignore dirs
3. Fix bugs

Version 2.5.1
-------------

Release on Jan 7, 2017

Happy New Year.

1. Fix Content-Type detection
2. Ensure current version of pyinotify is installed before using

Version 2.5.0
-------------

Released on Nov 16, 2016

1. wait parameter can be float via Todd Wolfson
2. Option to disable liveCSS via Yunchi Luo
3. Django management command via Marc-Stefan Cassola

Version 2.4.1
-------------

Released on Jan 19, 2016

1. Allow other hostname with JS script location.hostname
2. Expose delay parameter in command line tool
3. Server.watch accept ignore parameter

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

Version 0.6
------------
Release on Jun 18th, 2012

+ Add static server, 127.0.0.1:35729

Version 0.5
-----------
Release on Jun 18th, 2012

+ support for python3

Version 0.4
-----------
Release on May 8th, 2012

+ bugfix for notify (sorry)

Version 0.3
-----------
Release on May 6th, 2012

+ bugfix for compiler alias
+ raise error for CommandCompiler
+ add command-line feature
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
