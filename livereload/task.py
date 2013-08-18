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

try:
    import pyinotify
    from tornado import ioloop

    class TaskEventHandler(pyinotify.ProcessEvent):
        def my_init(self, **kwargs):
            self.func = kwargs['func']

        def process_default(self, event):
            if Task.watch():
                self.func()

    HAS_PYINOTIFY = True
except ImportError:
    HAS_PYINOTIFY = False

IGNORE = [
    '.pyc', '.pyo', '.o', '.swp'
]


class Task(object):
    tasks = {}
    _modified_times = {}
    last_modified = None
    if HAS_PYINOTIFY:
        wm = pyinotify.WatchManager()
        notifier = None

    @classmethod
    def add(cls, path, func=None):
        logging.info('Add task: %s' % path)
        if HAS_PYINOTIFY:
            cls.wm.add_watch(path, pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MODIFY, rec=True, do_glob=True, auto_add=True)
        cls.tasks[path] = func

    @classmethod
    def start(cls, func):
        if HAS_PYINOTIFY:
            if not cls.notifier:
                cls.notifier = pyinotify.TornadoAsyncNotifier(cls.wm, ioloop.IOLoop.instance(), default_proc_fun=TaskEventHandler(func=func))
                Task.watch()  # initial run so we don't miss the first change
        return HAS_PYINOTIFY

    @classmethod
    def watch(cls):
        _changed = False
        for path in cls.tasks:
            if cls.is_changed(path):
                _changed = True
                func = cls.tasks[path]
                func and func()

        return _changed

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
                return True

            if path in cls._modified_times and \
               cls._modified_times[path] != modified:
                logging.info('file changed: %s' % path)
                cls._modified_times[path] = modified
                cls.last_modified = path
                return True

            cls._modified_times[path] = modified
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

        if os.path.isfile(path):
            return is_file_changed(path)
        elif os.path.isdir(path):
            return is_folder_changed(path)
        else:
            return is_glob_changed(path)
        return False
