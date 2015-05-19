# -*- coding: utf-8 -*-
"""
    livereload.handlers
    ~~~~~~~~~~~~~~~~~~~

    HTTP and WebSocket handlers for livereload.

    :copyright: (c) 2013 - 2015 by Hsiaoming Yang
"""

import os
import time
import logging
from pkg_resources import resource_string
from tornado import web
from tornado import ioloop
from tornado import escape
from tornado.websocket import WebSocketHandler
from tornado.util import ObjectDict

logger = logging.getLogger('livereload')


class LiveReloadHandler(WebSocketHandler):
    waiters = set()
    watcher = None
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

    def poll_tasks(self):
        filepath, delay = self.watcher.examine()
        if not filepath or delay == 'forever':
            return
        reload_time = 3

        if delay:
            reload_time = max(3 - delay, 1)
        if filepath == '__livereload__':
            reload_time = 0

        if time.time() - self._last_reload_time < reload_time:
            # if you changed lot of files in one time
            # it will refresh too many times
            logger.info('Ignore: %s', filepath)
            return
        if delay:
            loop = ioloop.IOLoop.current()
            loop.call_later(delay, self.watch_tasks)
        else:
            self.watch_tasks()

    def watch_tasks(self):
        logger.info(
            'Reload %s waiters: %s',
            len(self.waiters),
            self.watcher.filepath,
        )

        msg = {
            'command': 'reload',
            'path': self.watcher.filepath or '*',
            'liveCSS': True
        }

        self._last_reload_time = time.time()
        for waiter in LiveReloadHandler.waiters:
            try:
                waiter.write_message(msg)
            except:
                logger.error('Error sending message', exc_info=True)
                LiveReloadHandler.waiters.remove(waiter)

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

            if not LiveReloadHandler._last_reload_time:
                if not self.watcher._tasks:
                    logger.info('Watch current working directory')
                    self.watcher.watch(os.getcwd())

                LiveReloadHandler._last_reload_time = time.time()
                logger.info('Start watching changes')
                if not self.watcher.start(self.poll_tasks):
                    ioloop.PeriodicCallback(self.poll_tasks, 800).start()


class LiveReloadJSHandler(web.RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        self.write(resource_string(__name__, 'vendors/livereload.js'))


class ForceReloadHandler(web.RequestHandler):
    def get(self):
        msg = {
            'command': 'reload',
            'path': self.get_argument('path', default=None) or '*',
            'liveCSS': True,
            'liveImg': True
        }
        for waiter in LiveReloadHandler.waiters:
            try:
                waiter.write_message(msg)
            except:
                logger.error('Error sending message', exc_info=True)
                LiveReloadHandler.waiters.remove(waiter)
        self.write('ok')


class StaticFileHandler(web.StaticFileHandler):
    def should_return_304(self):
        return False
