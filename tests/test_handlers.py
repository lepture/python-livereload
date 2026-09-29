import os
import tempfile
import unittest

from tornado import web
from tornado.testing import AsyncHTTPTestCase

from livereload.cli import parser
from livereload.handlers import StaticFileHandler
from livereload.server import Server


class StaticCacheTestCase(AsyncHTTPTestCase):
    allow_cache = False

    def get_app(self):
        self.tmp = tempfile.TemporaryDirectory()
        for name in ('index.html', 'app.js'):
            with open(os.path.join(self.tmp.name, name), 'w') as f:
                f.write('<html><head></head></html>')
        server = Server()
        server.root = self.tmp.name
        server.default_filename = 'index.html'
        server.allow_cache = self.allow_cache
        return web.Application(server.get_web_handlers(b''))

    def tearDown(self):
        super().tearDown()
        self.tmp.cleanup()


class TestNoCacheByDefault(StaticCacheTestCase):
    def test_static_files_are_not_cached(self):
        for path in ('/', '/index.html', '/app.js'):
            response = self.fetch(path)
            assert response.code == 200
            assert response.headers.get('Cache-Control') == 'no-cache'

    def test_versioned_urls_keep_tornado_max_age(self):
        response = self.fetch('/app.js?v=1')
        assert response.headers['Cache-Control'].startswith('max-age=')


class TestAllowCache(StaticCacheTestCase):
    allow_cache = True

    def test_no_cache_control_header(self):
        response = self.fetch('/app.js')
        assert response.code == 200
        assert 'Cache-Control' not in response.headers


class PresetHeaderHandler(StaticFileHandler):
    # As Server.setHeader does, set the header in set_default_headers
    def set_default_headers(self):
        self.set_header('Cache-Control', 'max-age=60')


class TestPresetCacheControl(AsyncHTTPTestCase):
    def get_app(self):
        self.tmp = tempfile.TemporaryDirectory()
        with open(os.path.join(self.tmp.name, 'app.js'), 'w') as f:
            f.write('')
        return web.Application([
            (r'/(.*)', PresetHeaderHandler, {'path': self.tmp.name}),
        ])

    def tearDown(self):
        super().tearDown()
        self.tmp.cleanup()

    def test_existing_value_is_kept(self):
        response = self.fetch('/app.js')
        assert response.headers['Cache-Control'] == 'max-age=60'


class TestCliAllowCache(unittest.TestCase):
    def test_defaults_to_false(self):
        assert parser.parse_args([]).allow_cache is False

    def test_flag(self):
        assert parser.parse_args(['--allow-cache']).allow_cache is True
