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
    def _check_file(cls, path):
        try:
            modified = os.stat(path).st_mtime
        except:
            return False
        if path not in cls._modified_times:
            cls._modified_times[path] = modified
            return False
        if cls._modified_times[path] != modified:
            cls._modified_times[path] = modified
            return True
        return False

    @classmethod
    def _add_task(cls, path, func=None):
        for ext in IGNORE:
            if not path.endswith(ext):
                cls.tasks[path] = func

    @classmethod
    def add(cls, path, func=None):
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                #: don't watch version control dirs
                if '.git' in dirs:
                    dirs.remove('.git')
                if '.hg' in dirs:
                    dirs.remove('.hg')
                if '.svn' in dirs:
                    dirs.remove('.svn')
                for f in files:
                    cls._add_task(os.path.join(root, f), func)
        elif os.path.isfile(path):
            cls._add_task(path, func)
        else:
            for p in glob.glob(path):
                cls._add_task(p, func)

    @classmethod
    def watch(cls):
        for path in cls.tasks:
            if cls._check_file(path):
                func = cls.tasks[path]
                if func:
                    func()
                return path

        return False
