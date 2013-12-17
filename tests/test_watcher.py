#!/usr/bin/python

import os
import time
import shutil
from livereload.watcher import Watcher

tmpdir = os.path.join(os.path.dirname(__file__), 'tmp')


class TestWatcher(object):

    def setUp(self):
        if os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)
        os.mkdir(tmpdir)

    def test_watch_dir(self):
        os.mkdir(os.path.join(tmpdir, '.git'))
        os.mkdir(os.path.join(tmpdir, '.hg'))
        os.mkdir(os.path.join(tmpdir, '.svn'))
        os.mkdir(os.path.join(tmpdir, '.cvs'))

        watcher = Watcher()
        watcher.watch(tmpdir)
        assert watcher.is_changed(tmpdir) is False

        with open(os.path.join(tmpdir, 'foo'), 'w') as f:
            f.write('')

        assert watcher.is_changed(tmpdir)
        assert watcher.is_changed(tmpdir) is False

    def test_watch_file(self):
        watcher = Watcher()
        watcher.count = 0

        filepath = os.path.join(tmpdir, 'foo')
        with open(filepath, 'w') as f:
            f.write('')

        def add_count():
            watcher.count += 1

        watcher.watch(filepath, add_count)
        assert watcher.is_changed(filepath)

        # sleep 1 second so that mtime will be different
        time.sleep(1)

        with open(filepath, 'w') as f:
            f.write('')

        assert watcher.examine() == os.path.abspath(filepath)
        assert watcher.count == 1

    def test_watch_glob(self):
        watcher = Watcher()
        watcher.watch(tmpdir + '/*')
        assert watcher.examine() is None

        with open(os.path.join(tmpdir, 'foo.pyc'), 'w') as f:
            f.write('')

        assert watcher.examine() is None

        filepath = os.path.join(tmpdir, 'foo')

        with open(filepath, 'w') as f:
            f.write('')

        assert watcher.examine() == os.path.abspath(filepath)
