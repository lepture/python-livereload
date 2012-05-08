#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
ROOT = os.path.dirname(__file__)
from setuptools import setup, find_packages
import livereload

setup(
    name='livereload',
    version=livereload.__version__,
    author='Hsiaoming Yang',
    author_email='lepture@me.com',
    url='http://lepture.com/project/livereload/',
    packages=find_packages(),
    description='Python LiveReload is an awesome tool for web developers',
    long_description=livereload.__doc__,
    entry_points={
        'console_scripts': ['livereload= livereload.app:main'],
    },
    install_requires=[
        'tornado',
    ],
    include_package_data=True,
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
    ]
)
