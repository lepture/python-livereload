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
from collections import defaultdict

IGNORE = [
    '.pyc', '.pyo', '.o', '.swp'
]


class Task(object):
    tasks = {}
    _modified_times = {}
    _modified_files = defaultdict(list) # a file/glob : list of files

    @classmethod
    def add(cls, path, func=None):
        logging.info('Add task: %s' % path)
        cls.tasks[path] = func

    @classmethod
    def watch(cls):
        _changed = False
        for path in cls.tasks:
            if cls.is_changed(path):
                _changed = True
                func = cls.tasks[path]
                func and func(modified_path = cls._modified_files[path][0])

        return _changed

    @classmethod
    def is_changed(cls, path):
        def is_file_changed(file_path):
            if not os.path.isfile(file_path):
                return False

            _, ext = os.path.splitext(file_path)
            if ext in IGNORE:
                return False

            modified = int(os.stat(file_path).st_mtime)

            if file_path not in cls._modified_times:
                cls._modified_times[file_path] = modified
                return False

            if file_path in cls._modified_times and \
               cls._modified_times[file_path] != modified:
                logging.info('file changed: %s' % file_path)
                cls._modified_times[file_path] = modified
                cls._modified_files[path].append(file_path)
                return True

            cls._modified_times[file_path] = modified
            return False

        def is_folder_changed(path):
            _changed = False
            for root, dirs, files in os.walk(path, followlinks=True):
                if '.git' in dirs:
                    dirs.remove('.git')
                if '.hg' in dirs:
                    dirs.remove('.hg')
                if '.svn' in dirs:
                    dirs.remove('.svn')
                if '.cvs' in dirs:
                    dirs.remove('.cvs')

                for f in files:
                    if is_file_changed(os.path.join(root, f)):
                        _changed = True

            return _changed

        def is_glob_changed(path):
            _changed = False
            for f in glob.glob(path):
                if is_file_changed(f):
                    _changed = True

            return _changed

        cls._modified_files[path] = []

        if os.path.isfile(path):
            return is_file_changed(path)
        elif os.path.isdir(path):
            return is_folder_changed(path)
        else:
            return is_glob_changed(path)
        return False
