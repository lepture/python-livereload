#!/usr/bin/env python
# -*- coding: utf-8 -*-

import livereload
from setuptools import setup
from email.utils import parseaddr
author, author_email = parseaddr(livereload.__author__)

setup(
    name='livereload',
    version=livereload.__version__,
    author=author,
    author_email=author_email,
    url=livereload.__homepage__,
    packages=['livereload'],
    description='Python LiveReload is an awesome tool for web developers',
    long_description=livereload.__doc__,
    scripts=[
        'bin/livereload',
    ],
    install_requires=[
        'tornado', 'docopt',
    ],
    license='BSD',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment :: Mozilla',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Debuggers',
    ]
)
