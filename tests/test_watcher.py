#!/usr/bin/python

import os
import time
import shutil
import unittest
from livereload.watcher import get_watcher_class

Watcher = get_watcher_class()

tmpdir = os.path.join(os.path.dirname(__file__), 'tmp')


class TestWatcher(unittest.TestCase):

    def setUp(self):
        if os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)
        os.mkdir(tmpdir)

    def tearDown(self):
        shutil.rmtree(tmpdir)

    def test_watch_dir(self):
        os.mkdir(os.path.join(tmpdir, '.git'))
        os.mkdir(os.path.join(tmpdir, '.hg'))
        os.mkdir(os.path.join(tmpdir, '.svn'))
        os.mkdir(os.path.join(tmpdir, '.cvs'))

        watcher = Watcher()
        watcher.watch(tmpdir)
        assert watcher.is_changed(tmpdir) is False

        # sleep 1 second so that mtime will be different
        time.sleep(1)

        with open(os.path.join(tmpdir, 'foo'), 'w') as f:
            f.write('')

        assert watcher.is_changed(tmpdir)
        assert watcher.is_changed(tmpdir) is False

    def test_watch_file(self):
        watcher = Watcher()
        watcher.count = 0

        # sleep 1 second so that mtime will be different
        time.sleep(1)

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

        rv = watcher.examine()
        assert rv[0] == os.path.abspath(filepath)
        assert watcher.count == 1

    def test_watch_glob(self):
        watcher = Watcher()
        watcher.watch(tmpdir + '/*')
        assert watcher.examine() == (None, None)

        with open(os.path.join(tmpdir, 'foo.pyc'), 'w') as f:
            f.write('')

        assert watcher.examine() == (None, None)

        filepath = os.path.join(tmpdir, 'foo')

        with open(filepath, 'w') as f:
            f.write('')

        rv = watcher.examine()
        assert rv[0] == os.path.abspath(filepath)

    def test_watch_ignore(self):
        watcher = Watcher()
        watcher.watch(tmpdir + '/*', ignore=lambda o: o.endswith('.ignore'))
        assert watcher.examine() == (None, None)

        with open(os.path.join(tmpdir, 'foo.ignore'), 'w') as f:
            f.write('')

        assert watcher.examine() == (None, None)
