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
        # TODO: This doesn't seem necessary; test passes without it
        time.sleep(1)

        filepath = os.path.join(tmpdir, 'foo')

        with open(filepath, 'w') as f:
            f.write('')

        assert watcher.is_changed(tmpdir)
        assert watcher.is_changed(tmpdir) is False

        os.remove(filepath)
        assert watcher.is_changed(tmpdir)
        assert watcher.is_changed(tmpdir) is False

    def test_watch_file(self):
        watcher = Watcher()
        watcher.count = 0

        # sleep 1 second so that mtime will be different
        # TODO: This doesn't seem necessary; test passes without it
        time.sleep(1)

        filepath = os.path.join(tmpdir, 'foo')
        with open(filepath, 'w') as f:
            f.write('')

        def add_count():
            watcher.count += 1

        watcher.watch(filepath, add_count)
        assert watcher.is_changed(filepath)
        assert watcher.is_changed(filepath) is False

        # sleep 1 second so that mtime will be different
        # TODO: This doesn't seem necessary; test passes without it
        time.sleep(1)

        with open(filepath, 'w') as f:
            f.write('')

        abs_filepath = os.path.abspath(filepath)
        assert watcher.examine() == (abs_filepath, None)
        assert watcher.examine() == (None, None)
        assert watcher.count == 1

        os.remove(filepath)
        assert watcher.examine() == (abs_filepath, None)
        assert watcher.examine() == (None, None)
        assert watcher.count == 2

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

        abs_filepath = os.path.abspath(filepath)
        assert watcher.examine() == (abs_filepath, None)
        assert watcher.examine() == (None, None)

        os.remove(filepath)
        assert watcher.examine() == (abs_filepath, None)
        assert watcher.examine() == (None, None)

    def test_watch_ignore(self):
        watcher = Watcher()
        watcher.watch(tmpdir + '/*', ignore=lambda o: o.endswith('.ignore'))
        assert watcher.examine() == (None, None)

        with open(os.path.join(tmpdir, 'foo.ignore'), 'w') as f:
            f.write('')

        assert watcher.examine() == (None, None)

    def test_watch_multiple_dirs(self):
        first_dir = os.path.join(tmpdir, 'first')
        second_dir = os.path.join(tmpdir, 'second')

        watcher = Watcher()

        os.mkdir(first_dir)
        watcher.watch(first_dir)
        assert watcher.examine() == (None, None)

        first_path = os.path.join(first_dir, 'foo')
        with open(first_path, 'w') as f:
            f.write('')
        assert watcher.examine() == (first_path, None)
        assert watcher.examine() == (None, None)

        os.mkdir(second_dir)
        watcher.watch(second_dir)
        assert watcher.examine() == (None, None)

        second_path = os.path.join(second_dir, 'bar')
        with open(second_path, 'w') as f:
            f.write('')
        assert watcher.examine() == (second_path, None)
        assert watcher.examine() == (None, None)

        with open(first_path, 'a') as f:
            f.write('foo')
        assert watcher.examine() == (first_path, None)
        assert watcher.examine() == (None, None)

        os.remove(second_path)
        assert watcher.examine() == (second_path, None)
        assert watcher.examine() == (None, None)
