# -*- coding: utf-8 -*-
"""
    livereload.handlers
    ~~~~~~~~~~~~~~~~~~~

    HTTP and WebSocket handlers for livereload.

    :copyright: (c) 2013 by Hsiaoming Yang
    :license: BSD, see LICENSE for more details.
"""

import os
import time
import logging
from tornado import web
from tornado import ioloop
from tornado import escape
from tornado.websocket import WebSocketHandler
from tornado.util import ObjectDict

logger = logging.getLogger('livereload')


class LiveReloadHandler(WebSocketHandler):
    waiters = set()
    watcher = None
    live_css = None
    _last_reload_time = None

    def allow_draft76(self):
        return True

    def check_origin(self, origin):
        return True

    def on_close(self):
        if self in LiveReloadHandler.waiters:
            LiveReloadHandler.waiters.remove(self)

    def send_message(self, message):
        if isinstance(message, dict):
            message = escape.json_encode(message)

        try:
            self.write_message(message)
        except:
            logger.error('Error sending message', exc_info=True)

    @classmethod
    def start_tasks(cls):
        if cls._last_reload_time:
            return

        if not cls.watcher._tasks:
            logger.info('Watch current working directory')
            cls.watcher.watch(os.getcwd())

        cls._last_reload_time = time.time()
        logger.info('Start watching changes')
        if not cls.watcher.start(cls.poll_tasks):
            logger.info('Start detecting changes')
            ioloop.PeriodicCallback(cls.poll_tasks, 800).start()

    @classmethod
    def poll_tasks(cls):
        filepath, delay = cls.watcher.examine()
        if not filepath or delay == 'forever' or not cls.waiters:
            return
        reload_time = 3

        if delay:
            reload_time = max(3 - delay, 1)
        if filepath == '__livereload__':
            reload_time = 0

        if time.time() - cls._last_reload_time < reload_time:
            # if you changed lot of files in one time
            # it will refresh too many times
            logger.info('Ignore: %s', filepath)
            return
        if delay:
            loop = ioloop.IOLoop.current()
            loop.call_later(delay, cls.reload_waiters)
        else:
            cls.reload_waiters()

    @classmethod
    def reload_waiters(cls, path=None):
        logger.info(
            'Reload %s waiters: %s',
            len(cls.waiters),
            cls.watcher.filepath,
        )

        if path is None:
            path = cls.watcher.filepath or '*'

        msg = {
            'command': 'reload',
            'path': path,
            'liveCSS': cls.live_css,
            'liveImg': True,
        }

        cls._last_reload_time = time.time()
        for waiter in cls.waiters.copy():
            try:
                waiter.write_message(msg)
            except:
                logger.error('Error sending message', exc_info=True)
                cls.waiters.remove(waiter)

    def on_message(self, message):
        """Handshake with livereload.js

        1. client send 'hello'
        2. server reply 'hello'
        3. client send 'info'
        """
        message = ObjectDict(escape.json_decode(message))
        if message.command == 'hello':
            handshake = {
                'command': 'hello',
                'protocols': [
                    'http://livereload.com/protocols/official-7',
                ],
                'serverName': 'livereload-tornado',
            }
            self.send_message(handshake)

        if message.command == 'info' and 'url' in message:
            logger.info('Browser Connected: %s' % message.url)
            LiveReloadHandler.waiters.add(self)


class LiveReloadJSHandler(web.RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        root = os.path.abspath(os.path.dirname(__file__))
        js_file = os.path.join(root, 'vendors/livereload.js')
        with open(js_file, 'rb') as f:
            self.write(f.read())


class ForceReloadHandler(web.RequestHandler):
    def get(self):
        path = self.get_argument('path', default=None) or '*'
        LiveReloadHandler.reload_waiters(path)
        self.write('ok')


class StaticFileHandler(web.StaticFileHandler):
    """Override of tornado.web.StaticFileHandler, adding cache control features

    Additional Initialization Parameters:
        cache_control   A string containing the cache control options requested.
                        Valid examples : "auto" ; "no-304, no-etag" ; "no-cache" ; "  no-cache no-304"

    Cache Control Options:
        none            Disable all cache control options
        auto            Enable default cache control options : "no-304"
        full            Enable all cache control options
        no-304          Server will never return a HTTP 304
        no-etag         Server will not provide an ETag in the response headers
        no-cache        Server explicitly adds `Cache-Control` headers specifying `no-cache` for the browser
    """

    CC_NONE, CC_AUTO, CC_FULL = 'none', 'auto', 'full'

    _cc_no_304 = 'no-304'
    _cc_no_etag = 'no-etag'
    _cc_no_cache = 'no-cache'

    _CC_REPLACE_AUTO = _cc_no_304
    _CC_REPLACE_FULL = ", ".join([_cc_no_304, _cc_no_etag, _cc_no_cache])
    
    def initialize(self, path, default_filename=None, cache_control=CC_AUTO):
        super(StaticFileHandler, self).initialize(path, default_filename)

        cache_control = cache_control.replace(self.CC_AUTO, self._CC_REPLACE_AUTO)
        cache_control = cache_control.replace(self.CC_FULL, self._CC_REPLACE_FULL)

        self._cc_no_304 = self._cc_no_304 in cache_control
        self._cc_no_etag = self._cc_no_etag in cache_control
        self._cc_no_cache = self._cc_no_cache in cache_control

    def should_return_304(self):
        return False if self._cc_no_304 else super(StaticFileHandler, self).should_return_304()

    def compute_etag(self):
        return None if self._cc_no_etag else super(StaticFileHandler, self).compute_etag()

    def set_extra_headers(self, path):
        if self._cc_no_cache:
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

