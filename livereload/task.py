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
import logging

IGNORE = [
    '.pyc', '.pyo', '.o', '.swp'
]


class Task(object):
    tasks = {}
    _modified_times = {}

    @classmethod
    def add(cls, path, func=None):
        logging.info('Add task: %s' % path)
        cls.tasks[path] = func

    @classmethod
    def watch(cls):
        result = False
        changes = []

        for path in cls.tasks:
            if cls.is_changed(path):
                result = True
                changes.append(path)
                func = cls.tasks[path]
                if func:
                    func()

        return result and changes

    @classmethod
    def is_changed(cls, path):
        def is_file_changed(path):
            if not os.path.isfile(path):
                return False

            _, ext = os.path.splitext(path)
            if ext in IGNORE:
                return False

            modified = int(os.stat(path).st_mtime)

            if path not in cls._modified_times:
                cls._modified_times[path] = modified
                return False

            if path in cls._modified_times and \
               cls._modified_times[path] != modified:
                logging.info('file changed: %s' % path)
                cls._modified_times[path] = modified
                return True

            cls._modified_times[path] = modified
            return False

        def is_folder_changed(path):
            for root, dirs, files in os.walk(path):
                if '.git' in dirs:
                    dirs.remove('.git')
                if '.hg' in dirs:
                    dirs.remove('.hg')
                if '.svn' in dirs:
                    dirs.remove('.svn')
                if '.cvs' in dirs:
                    dirs.remove('.cvs')

                for f in files:
                    path = os.path.join(root, f)
                    if is_file_changed(path):
                        return True

            return False

        def is_glob_changed(path):
            for f in glob.glob(path):
                if is_file_changed(f):
                    return True

            return False

        if os.path.isfile(path):
            return is_file_changed(path)
        elif os.path.isdir(path):
            return is_folder_changed(path)
        else:
            return is_glob_changed(path)
        return False
