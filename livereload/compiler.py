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


class BaseCompiler(object):
    """BaseCompiler

    BaseCompiler defines the basic syntax of a Compiler.

    >>> c = BaseCompiler('a')
    >>> c.write('b')  #: write compiled code to 'b'
    >>> c.append('c')  #: append compiled code to 'c'
    """
    def __init__(self, path):
        self.path = path

    def _get_code(self):
        f = open(self.path)
        code = f.read()
        f.close()
        return code

    def write(self, output):
        make_folder(output)
        f = open(output, 'w')
        f.write(self._get_code())
        f.close()

    def append(self, output):
        make_folder(output)
        f = open(output, 'a')
        f.write(self._get_code())
        f.close()


class _CommandCompiler(BaseCompiler):
    command = ''
    command_options = ''

    def _get_code(self):
        cmd = [self.command, self.command_options, self.path]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        return stdout


class LessCompiler(_CommandCompiler):
    command = 'lessc'
    command_options = '--compress'


@functools.partial
def lessc(path, output, mode='w'):
    c = LessCompiler(path)
    if mode == 'a':
        c.append(output)
    else:
        c.write(output)
    return


class UglifyJSCompiler(_CommandCompiler):
    command = 'uglifyjs'
    command_options = '-nc'


@functools.partial
def uglifyjs(path, output, mode='w'):
    c = UglifyJSCompiler(path)
    if mode == 'a':
        c.append(output)
    else:
        c.write(output)
    return


class SlimmerCompiler(BaseCompiler):
    def _get_code(self):
        import slimmer
        f = open(self.path)
        code = f.read()
        f.close()
        if self.path.endswith('.css'):
            return slimmer.css_slimmer(code)
        if self.path.endswith('.js'):
            return slimmer.js_slimmer(code)
        if self.path.endswith('.html'):
            return slimmer.xhtml_slimmer(code)
        return code


@functools.partial
def slimmer(path, output, mode='w'):
    c = SlimmerCompiler(path)
    if mode == 'a':
        c.append(output)
    else:
        c.write(output)
    return
