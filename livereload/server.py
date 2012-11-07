# -*- coding: utf-8 -*-

"""livereload.app

Core Server of LiveReload.
"""

import os
import logging
import mimetypes
from tornado import ioloop
from tornado import escape
from tornado import websocket
from tornado.web import RequestHandler, Application
from tornado.util import ObjectDict
from tornado.options import enable_pretty_logging
from livereload.task import Task


PORT = 35729
LIVERELOAD = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'livereload.js',
)


class LiveReloadHandler(websocket.WebSocketHandler):
    waiters = set()
    _watch_running = False

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

    def watch_tasks(self):
        changes = Task.watch()
        if not changes:
            return

        logging.info(
            'Reload %s waiters'
            '\nChanged %s'
            % (len(LiveReloadHandler.waiters), changes)
        )
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
            if not LiveReloadHandler._watch_running:
                if os.path.exists('Guardfile'):
                    logging.info('Reading Guardfile')
                    execfile('Guardfile')
                else:
                    logging.info('No Guardfile')
                    Task.add(os.getcwd())

                LiveReloadHandler._watch_running = True
                logging.info('Start watching changes')
                ioloop.PeriodicCallback(self.watch_tasks, 800).start()


class IndexHandler(RequestHandler):
    def get(self, path='/'):
        abspath = os.path.join(os.path.abspath('.'), path.lstrip('/'))
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
        if abspath.endswith('/'):
            filepath = os.path.join(abspath, 'index.html')
            if not os.path.exists(filepath):
                self.create_index(abspath)
                return
        elif not os.path.exists(abspath):
            filepath = abspath + '.html'

        if os.path.exists(filepath):
            for line in open(filepath):
                if '</head>' in line:
                    self.inject_livereload()
                self.write(line)
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


def start(port):
    global PORT
    PORT = port
    logging.getLogger().setLevel(logging.INFO)
    enable_pretty_logging()
    app = Application(handlers=handlers)
    app.listen(port)
    print('Start service at  127.0.0.1:%s' % port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start(8000)
