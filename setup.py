#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import livereload

setup(
    name='livereload',
    version=livereload.__version__,
    author='Hsiaoming Yang',
    author_email='lepture@me.com',
    url='http://lepture.com/project/livereload/',
    packages=find_packages(),
    description='python-livereload is a tool for july project',
    entry_points={
        'console_scripts': ['livereload= livereload.app:main'],
    },
    install_requires=[
        'tornado',
    ],
    include_package_data=True,
    license='BSD License',
)
