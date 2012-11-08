#!/usr/bin/python

"""livereload.compiler

Provides a set of compilers for web developers.

Available compilers now:

+ less
+ uglifyjs
+ slimmer
"""

import os
import functools
import logging
from subprocess import Popen, PIPE


def make_folder(dest):
    folder = os.path.split(dest)[0]
    if not folder:
        return
    if os.path.isdir(folder):
        return
    try:
        os.makedirs(folder)
    except:
        pass


def _get_http_file(url, build_dir='build/assets'):
    import hashlib
    key = hashlib.md5(url).hexdigest()
    filename = os.path.join(os.getcwd(), build_dir, key)
    if os.path.exists(filename):
        return filename
    make_folder(filename)

    import urllib
    print('Downloading: %s' % url)
    urllib.urlretrieve(url, filename)
    return filename


class BaseCompiler(object):
    """BaseCompiler

    BaseCompiler defines the basic syntax of a Compiler.

    >>> c = BaseCompiler('a')
    >>> c.write('b')  #: write compiled code to 'b'
    >>> c.append('c')  #: append compiled code to 'c'
    """
    def __init__(self, path):
        self.filetype = os.path.splitext(path)[1]

        if path.startswith('http://') or path.startswith('https://'):
            path = _get_http_file(path)

        self.path = path

    def _get_code(self):
        f = open(self.path)
        code = f.read()
        f.close()
        return code

    def write(self, output):
        """write code to output"""
        logging.info('write %s' % output)
        make_folder(output)
        f = open(output, 'w')
        f.write(self._get_code())
        f.close()

    def append(self, output):
        """append code to output"""
        logging.info('append %s' % output)
        make_folder(output)
        f = open(output, 'a')
        f.write(self._get_code())
        f.close()


class _CommandCompiler(BaseCompiler):
    command = ''

    def _get_code(self):
        cmd = self.command.split()
        cmd.append(self.path)

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            raise Exception(stderr)
        #: stdout is bytes, decode for python3
        return stdout.decode()


class LessCompiler(_CommandCompiler):
    command = 'lessc --compress'


def lessc(path, output, mode='w'):
    def _compile(path, output, mode):
        c = LessCompiler(path)
        if mode == 'a':
            c.append(output)
            return
        c.write(output)
        return
    return functools.partial(_compile, path, output, mode)


class UglifyJSCompiler(_CommandCompiler):
    command = 'uglifyjs -nc'


def uglifyjs(path, output, mode='w'):
    def _compile(path, output, mode):
        c = UglifyJSCompiler(path)
        if mode == 'a':
            c.append(output)
            return
        c.write(output)
        return
    return functools.partial(_compile, path, output, mode)


class SlimmerCompiler(BaseCompiler):
    def _get_code(self):
        import slimmer
        f = open(self.path)
        code = f.read()
        f.close()
        if self.filetype == '.css':
            return slimmer.css_slimmer(code)
        if self.filetype == '.js':
            return slimmer.js_slimmer(code)
        if self.filetype == '.html':
            return slimmer.xhtml_slimmer(code)
        return code


def slimmer(path, output, mode='w'):
    def _compile(path, output, mode):
        c = SlimmerCompiler(path)
        if mode == 'a':
            c.append(output)
            return
        c.write(output)
        return
    return functools.partial(_compile, path, output, mode)


class RstCompiler(_CommandCompiler):
    command = 'rst2html.py'


def rstc(path, output, mode='w'):
    def _compile(path, output, mode):
        c = RstCompiler(path)
        if mode == 'a':
            c.append(output)
        else:
            c.write(output)
    return functools.partial(_compile, path, output, mode)
