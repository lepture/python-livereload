#!/usr/bin/env python

import re
from setuptools import setup


def fread(filepath):
    with open(filepath) as f:
        return f.read()


def version():
    content = fread('livereload/__init__.py')
    pattern = r"__version__ = '([0-9\.dev]*)'"
    m = re.findall(pattern, content)
    return m[0]


setup(
    name='livereload',
    version=version(),
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    url='https://github.com/lepture/python-livereload',
    packages=['livereload', 'livereload.management.commands'],
    description='Python LiveReload is an awesome tool for web developers',
    long_description_content_type='text/x-rst',
    long_description=fread('README.md'),
    entry_points={
        'console_scripts': [
            'livereload = livereload.cli:main',
        ]
    },
    install_requires=[
        'tornado',
    ],
    license='BSD',
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment :: Mozilla',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Debuggers',
    ]
)
