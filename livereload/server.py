# -*- coding: utf-8 -*-
"""
    livereload.server
    ~~~~~~~~~~~~~~~~~

    HTTP and WebSocket server for livereload.

    :copyright: (c) 2013 by Hsiaoming Yang
"""

import os
import sys
import logging
import time
import mimetypes
import webbrowser
import hashlib
from tornado import ioloop
from tornado import escape
from tornado import websocket
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, Application
from tornado.util import ObjectDict
from livereload.task import Task
from ._compat import to_bytes


class LiveReloadHandler(WebSocketHandler):
    waiters = set()
    _last_reload_time = None

    def allow_draft76(self):
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
            logging.error('Error sending message', exc_info=True)

    def poll_tasks(self):
        changes = Task.watch()
        if not changes:
            return
        self.watch_tasks()

    def watch_tasks(self):
        if time.time() - self._last_reload_time < 3:
            # if you changed lot of files in one time
            # it will refresh too many times
            logging.info('ignore this reload action')
            return

        logging.info('Reload %s waiters', len(self.waiters))

        msg = {
            'command': 'reload',
            'path': Task.last_modified or '*',
            'liveCSS': True
        }

        self._last_reload_time = time.time()
        for waiter in LiveReloadHandler.waiters:
            try:
                waiter.write_message(msg)
            except:
                logging.error('Error sending message', exc_info=True)
                LiveReloadHandler.waiters.remove(waiter)

    def on_message(self, message):
        """Handshake with livereload.js

        1. client send 'hello'
        2. server reply 'hello'
        3. client send 'info'

        http://help.livereload.com/kb/ecosystem/livereload-protocol
        """
        message = ObjectDict(escape.json_decode(message))
        if message.command == 'hello':
            handshake = {}
            handshake['command'] = 'hello'
            protocols = message.protocols
            protocols.append(
                'http://livereload.com/protocols/2.x-remote-control'
            )
            handshake['protocols'] = protocols
            handshake['serverName'] = 'livereload-tornado'
            self.send_message(handshake)

        if message.command == 'info' and 'url' in message:
            logging.info('Browser Connected: %s' % message.url)
            LiveReloadHandler.waiters.add(self)
            if not LiveReloadHandler._last_reload_time:
                if os.path.exists('Guardfile'):
                    logging.info('Reading Guardfile')
                    execfile('Guardfile', {})
                else:
                    logging.info('No Guardfile')
                    Task.add(os.getcwd())

                LiveReloadHandler._last_reload_time = time.time()
                logging.info('Start watching changes')
                if not Task.start(self.watch_tasks):
                    ioloop.PeriodicCallback(self.poll_tasks, 800).start()


class IndexHandler(RequestHandler):
    def initialize(self, root='.'):
        self._root = os.path.abspath(root)

    def get(self, path='/'):
        abspath = os.path.join(self._root, path.lstrip('/'))
        mime_type, encoding = mimetypes.guess_type(abspath)
        if not mime_type:
            mime_type = 'text/html'

        self.mime_type = mime_type
        self.set_header('Content-Type', mime_type)
        self.read_path(abspath)

    def inject_livereload(self):
        if self.mime_type != 'text/html':
            return
        ua = self.request.headers.get('User-Agent', 'bot').lower()
        if 'msie' not in ua:
            self.write('<script src="/livereload.js"></script>')

    def read_path(self, abspath):
        filepath = abspath
        if os.path.isdir(filepath):
            filepath = os.path.join(abspath, 'index.html')
            if not os.path.exists(filepath):
                self.create_index(abspath)
                return
        elif not os.path.exists(abspath):
            filepath = abspath + '.html'

        if not os.path.exists(filepath):
            return self.send_error(404)

        if self.mime_type == 'text/html':
            with open(filepath, 'r') as f:
                data = f.read()
            before, after = data.split('</head>')
            self.write(before)
            self.inject_livereload()
            self.write('</head>')
            self.write(after)
        else:
            with open(filepath, 'rb') as f:
                data = f.read()
            self.write(data)

        hasher = hashlib.sha1()
        hasher.update(to_bytes(data))
        self.set_header('Etag', '"%s"' % hasher.hexdigest())

    def create_index(self, root):
        self.inject_livereload()
        files = os.listdir(root)
        self.write('<ul>')
        for f in files:
            path = os.path.join(root, f)
            self.write('<li>')
            if os.path.isdir(path):
                self.write('<a href="%s/">%s</a>' % (f, f))
            else:
                self.write('<a href="%s">%s</a>' % (f, f))
            self.write('</li>')

        self.write('</ul>')


class LiveReloadJSHandler(RequestHandler):
    def initialize(self, port=35729):
        self._port = port

    def get(self):
        js = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'livereload.js',
        )
        self.set_header('Content-Type', 'application/javascript')
        with open(js, 'r') as f:
            for line in f:
                if '{{port}}' in line:
                    line = line.replace('{{port}}', str(self._port))
                self.write(line)


class ForceReloadHandler(RequestHandler):

    def get(self):
        logging.info('Recieved reload request')

        msg = {
            'command': 'reload',
            'path': '*',
            'liveCSS': True
        }

        for waiter in LiveReloadHandler.waiters:
            try:
                waiter.write_message(msg)
            except:
                logging.error('Error sending message', exc_info=True)
                LiveReloadHandler.waiters.remove(waiter)

        self.write("Success!")


def create_app(port=35729, root='.'):
    handlers = [
        (r'/livereload', LiveReloadHandler),
        (r'/livereload.js', LiveReloadJSHandler, dict(port=port)),
        (r'/reload', ForceReloadHandler),
        (r'(.*)', IndexHandler, dict(root=root)),
    ]
    return Application(handlers=handlers)


def start(port=35729, root='.', autoraise=False):
    try:
        from tornado.log import enable_pretty_logging
    except ImportError:
        from tornado.options import enable_pretty_logging

    logging.getLogger().setLevel(logging.INFO)
    enable_pretty_logging()

    app = create_app(port, root)
    app.listen(port)

    print('Serving path %s on 127.0.0.1:%s' % (root, port))

    if autoraise:
        webbrowser.open(
            'http://127.0.0.1:%s' % port, new=2, autoraise=True
        )
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('Shutting down...')


if __name__ == '__main__':
    start(8000)
