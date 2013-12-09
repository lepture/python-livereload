.. _installation:

Installation
============

This part of the documentation covers the installation of livereload.
The first step to using any software package is getting it properly installed.


Distribute & Pip
----------------

Installing livereload is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install livereload

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install livereload

But, you really `shouldn't do that <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.



Cheeseshop Mirror
-----------------

If the Cheeseshop is down, you can also install livereload from one of the
mirrors. `Crate.io <http://crate.io>`_ is one of them::

    $ pip install -i http://simple.crate.io/ livereload


Get the Code
------------

livereload is actively developed on GitHub, where the code is
`always available <https://github.com/lepture/python-livereload>`_.

You can either clone the public repository::

    git clone git://github.com/lepture/python-livereload.git

Download the `tarball <https://github.com/lepture/python-livereload/tarball/master>`_::

    $ curl -OL https://github.com/lepture/python-livereload/tarball/master

Or, download the `zipball <https://github.com/lepture/python-livereload/zipball/master>`_::

    $ curl -OL https://github.com/lepture/python-livereload/zipball/master


Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install
