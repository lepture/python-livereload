# -*- coding: utf-8 -*-

"""livereload.app

Core Server of LiveReload.
"""

import os
import logging
import time
import mimetypes
import webbrowser
import hashlib
from tornado import ioloop
from tornado import escape
from tornado import websocket
from tornado.web import RequestHandler, Application
from tornado.util import ObjectDict
try:
    from tornado.log import enable_pretty_logging
except ImportError:
    from tornado.options import enable_pretty_logging
from livereload.task import Task


PORT = 35729
ROOT = '.'
LIVERELOAD = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'livereload.js',
)


class LiveReloadHandler(websocket.WebSocketHandler):
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

    def get(self, path='/'):
        abspath = os.path.join(os.path.abspath(ROOT), path.lstrip('/'))
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

        if os.path.exists(filepath):
            if self.mime_type == 'text/html':
                f = open(filepath)
                data = f.read()
                f.close()
                before, after = data.split('</head>')
                self.write(before)
                self.inject_livereload()
                self.write('</head>')
                self.write(after)
            else:
                f = open(filepath, 'rb')
                data = f.read()
                f.close()
                self.write(data)

            hasher = hashlib.sha1()
            hasher.update(data)
            self.set_header('Etag', '"%s"' % hasher.hexdigest())
            return
        self.send_error(404)
        return

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
    def get(self):
        f = open(LIVERELOAD)
        self.set_header('Content-Type', 'application/javascript')
        for line in f:
            if '{{port}}' in line:
                line = line.replace('{{port}}', str(PORT))
            self.write(line)
        f.close()

handlers = [
    (r'/livereload', LiveReloadHandler),
    (r'/livereload.js', LiveReloadJSHandler),
    (r'(.*)', IndexHandler),
]


def start(port=35729, root='.', autoraise=False):
    global PORT
    PORT = port
    global ROOT
    if root is None:
        root = '.'
    ROOT = root
    logging.getLogger().setLevel(logging.INFO)
    enable_pretty_logging()
    app = Application(handlers=handlers)
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
