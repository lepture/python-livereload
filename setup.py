#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
ROOT = os.path.dirname(__file__)

import sys
kwargs = {}
kwargs['include_package_data'] = True
major, minor = sys.version_info[:2]
if major >= 3:
    kwargs['use_2to3'] = True

from setuptools import setup, find_packages
import livereload
from email.utils import parseaddr
author, author_email = parseaddr(livereload.__author__)

setup(
    name='livereload',
    version=livereload.__version__,
    author=author,
    author_email=author_email,
    url=livereload.__homepage__,
    packages=find_packages(),
    description='Python LiveReload is an awesome tool for web developers',
    long_description=livereload.__doc__,
    entry_points={
        'console_scripts': ['livereload= livereload.cli:main'],
    },
    install_requires=[
        'tornado', 'docopt',
    ],
    license=open(os.path.join(ROOT, 'LICENSE')).read(),
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
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Debuggers',
    ],
    **kwargs
)
