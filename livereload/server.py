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
import hashlib
from tornado import ioloop
from tornado import escape
from tornado import websocket
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, Application, FallbackHandler
from tornado.util import ObjectDict
from tornado.wsgi import WSGIContainer
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

        http://feedback.livereload.com/knowledgebase/articles/86174-livereload-protocol
        """
        message = ObjectDict(escape.json_decode(message))
        if message.command == 'hello':
            handshake = {}
            handshake['command'] = 'hello'
            handshake['protocols'] = [
                'http://livereload.com/protocols/official-7',
                'http://livereload.com/protocols/official-8',
                'http://livereload.com/protocols/official-9',
                'http://livereload.com/protocols/2.x-origin-version-negotiation',
                'http://livereload.com/protocols/2.x-remote-control'
            ]
            handshake['serverName'] = 'livereload-tornado'
            self.send_message(handshake)

        if message.command == 'info' and 'url' in message:
            logging.info('Browser Connected: %s' % message.url)
            LiveReloadHandler.waiters.add(self)
            if not LiveReloadHandler._last_reload_time:
                if os.path.exists('Guardfile'):
                    logging.info('Reading Guardfile')
                    execfile('Guardfile', {})
                elif Task.tasks:
                    # Tasks have been added through library-use.
                    logging.debug('Not loading any tasks, library-use.')
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

    def filepath(self, url):
        url = url.lstrip('/')
        url = os.path.join(self._root, url)

        if url.endswith('/'):
            url += 'index.html'
        elif not os.path.exists(url) and not url.endswith('.html'):
            url += '.html'

        if not os.path.exists(url):
            return None
        return url

    def get(self, path='/'):
        filepath = self.filepath(path)
        if not filepath and path.endswith('/'):
            rootdir = os.path.join(self._root, path.lstrip('/'))
            return self.create_index(rootdir)

        if not filepath:
            return self.send_error(404)

        mime_type, encoding = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = 'text/html'

        self.mime_type = mime_type
        self.set_header('Content-Type', mime_type)

        with open(filepath, 'r') as f:
            data = f.read()

        hasher = hashlib.sha1()
        hasher.update(to_bytes(data))
        self.set_header('Etag', '"%s"' % hasher.hexdigest())

        ua = self.request.headers.get('User-Agent', 'bot').lower()
        if mime_type == 'text/html' and 'msie' not in ua:
            data = data.replace(
                '</head>',
                '<script src="/livereload.js"></script></head>'
            )
        self.write(data)

    def create_index(self, root):
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


class Server(object):
    def __init__(self, wsgi_app=None, port=35729, root='.'):
        handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler, dict(port=port)),
        ]
        if wsgi_app:
            wsgi_app = WSGIContainer(wsgi_app)
            handlers.append(
                (r'.*', FallbackHandler, dict(fallback=wsgi_app))
            )
        else:
            handlers.append(
                (r'(.*)', IndexHandler, dict(root=root)),
            )

        self.app = Application(handlers=handlers)
        self.port = port

    def serve(self, autoraise=False):
        try:
            from tornado.log import enable_pretty_logging
        except ImportError:
            from tornado.options import enable_pretty_logging

        logging.getLogger().setLevel(logging.INFO)
        enable_pretty_logging()
        self.app.listen(self.port)

        print('Serving on 127.0.0.1:%s' % self.port)
        if autoraise:
            import webbrowser
            webbrowser.open(
                'http://127.0.0.1:%s' % self.port, new=2, autoraise=True
            )
        try:
            ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            print('Shutting down...')


if __name__ == '__main__':
    Server(port=8000).serve()
