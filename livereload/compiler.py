#!/usr/bin/python

import os
import subprocess


def get_subprocess_output(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout


def make_folder(dest):
    folder = os.path.split(dest)[0]
    if not os.path.isdir(folder):
        os.makedirs(folder)


class Compiler(object):
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


class _CommandCompiler(Compiler):
    command = ''
    command_options = ''

    def _get_code(self):
        cmd = [self.command, self.command_options, self.path]
        return get_subprocess_output(cmd)


class LessCompiler(_CommandCompiler):
    """LessCompiler

    >>> less = LessCompiler('style.less')
    >>> less.write('style.css')
    """

    command = 'lessc'
    command_options = '--compress'


class UglifyJSCompiler(_CommandCompiler):
    command = 'uglifyjs'
    command_options = '-nc'


class SlimmerCompiler(Compiler):
    def _get_code(self):
        import slimmer
        f = open(self.output)
        code = f.read()
        f.close()
        if self.path.endswith('.css'):
            return slimmer.css_slimmer(code)
        if self.path.endswith('.js'):
            return slimmer.js_slimmer(code)
        if self.path.endswith('.html'):
            return slimmer.xhtml_slimmer(code)
        return code
