# -*- coding: utf-8 -*-

"""livereload.task

Task management for LiveReload Server.

A basic syntax overview::

    from livereload.task import Task

    Task.add('file.css')

    def do_some_thing():
        pass

    Task.add('file.css', do_some_thing)
"""

import os
import glob

IGNORE = [
    '.pyc', '.pyo', '.o',
]


class Task(object):
    tasks = {}
    _modified_times = {}

    @classmethod
    def add(cls, path, func=None):
        cls.tasks[path] = func

    @classmethod
    def watch(cls):
        result = False
        changes = []
        for path in cls.tasks:
            if cls._checking(path):
                result = True
                changes.append(path)
                func = cls.tasks[path]
                if func:
                    func()

        return result and changes

    @classmethod
    def _check_file(cls, path):
        for ext in IGNORE:
            if path.endswith(ext):
                return False

        if not os.path.isfile(path):
            return False

        modified = os.stat(path).st_mtime

        if path not in cls._modified_times:
            cls._modified_times[path] = modified
            return False

        if path in cls._modified_times and \
           cls._modified_times[path] == modified:
            return False

        return True

    @classmethod
    def _checking(cls, path):
        if os.path.isfile(path):
            return cls._check_file(path)

        if os.path.isdir(path):
            result = False
            for root, dirs, files in os.walk(path):
                #: don't watch version control dirs
                if '.git' in dirs:
                    dirs.remove('.git')
                if '.hg' in dirs:
                    dirs.remove('.hg')
                if '.svn' in dirs:
                    dirs.remove('.svn')
                for f in files:
                    path = os.path.join(root, f)
                    result = cls._check_file(path) or result

            return result

        result = False
        for f in glob.glob(path):
            result = cls._check_file(f) or result

        return result
