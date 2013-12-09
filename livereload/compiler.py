#!/usr/bin/python
# -*- coding: utf-8 -*-

"""livereload.compiler

Provides a set of compilers for web developers.

Available compilers now:

+ less
+ coffee
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


class BaseCompiler(object):
    """BaseCompiler

    BaseCompiler defines the basic syntax of a Compiler.

    >>> c = BaseCompiler('a')
    >>> c.write('b')  #: write compiled code to 'b'
    >>> c.append('c')  #: append compiled code to 'c'
    """
    def __init__(self, path=None):
        if path:
            self.filetype = os.path.splitext(path)[1]
        self.path = path

    def get_code(self):
        f = open(self.path)
        code = f.read()
        f.close()
        return code

    def write(self, output):
        """write code to output"""
        logging.info('write %s' % output)
        make_folder(output)
        f = open(output, 'w')
        code = self.get_code()
        if code:
            f.write(code)
        f.close()

    def append(self, output):
        """append code to output"""
        logging.info('append %s' % output)
        make_folder(output)
        f = open(output, 'a')
        f.write(self.get_code())
        f.close()

    def __call__(self, output, mode='w'):
        if mode == 'a':
            self.append(output)
            return
        self.write(output)
        return


class CommandCompiler(BaseCompiler):
    def init_command(self, command, source=None):
        self.command = command
        self.source = source

    def get_code(self):
        cmd = self.command.split()
        if self.path:
            cmd.append(self.path)

        try:
            p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except OSError as e:
            logging.error(e)
            if e.errno == os.errno.ENOENT:  # file (command) not found
                logging.error("maybe you haven't installed %s", cmd[0])
            return None
        if self.source:
            stdout, stderr = p.communicate(input=self.source)
        else:
            stdout, stderr = p.communicate()
        if stderr:
            logging.error(stderr)
            return None
        #: stdout is bytes, decode for python3
        return stdout.decode()


class SlimmerCompiler(BaseCompiler):
    def get_code(self):
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
    _compile = SlimmerCompiler(path)
    return functools.partial(_compile, output, mode)


def shell(command, path=None, output=None, mode='w'):
    """Command shell command.

    Define a task in your Guardfile::

        Task.add('*.styl', shell('make stylus'))
    """
    if not output:
        output = os.devnull
    _compile = CommandCompiler(path)
    _compile.init_command(command)
    return functools.partial(_compile, output, mode)


def coffee(path, output, mode='w'):
    _compile = CommandCompiler(path)
    f = open(path)
    code = f.read()
    f.close()
    _compile.init_command('coffee --compile --stdio', code)
    return functools.partial(_compile, output, mode)
