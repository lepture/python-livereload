import os
import logging
import tornado.web
import tornado.options
import tornado.ioloop
from tornado.options import define, options
from tornado import escape
from tornado import websocket
from tornado.util import ObjectDict

ROOT = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(ROOT, 'static')

define('port', default=35729, type=int, help='livereload port')


class Task(object):
    tasks = {}
    _modified_times = {}

    @classmethod
    def _check_file(cls, path):
        try:
            modified = os.stat(path).st_mtime
        except:
            return False
        if path not in cls._modified_times:
            cls._modified_times[path] = modified
            return False
        if cls._modified_times[path] != modified:
            cls._modified_times[path] = modified
            return True
        return False

    @classmethod
    def add(cls, path, func=None):
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                #: don't watch version control dirs
                if '.git' in dirs:
                    dirs.remove('.git')
                if '.hg' in dirs:
                    dirs.remove('.hg')
                if '.svn' in dirs:
                    dirs.remove('.svn')
                for f in files:
                    p = os.path.join(root, f)
                    cls.tasks[p] = func
        else:
            cls.tasks[path] = func

    @classmethod
    def watch(cls):
        for path in cls.tasks:
            if cls._check_file(path):
                func = cls.tasks[path]
                if func:
                    func()
                return path

        return False


class LiveReloadHandler(websocket.WebSocketHandler):
    waiters = set()
    _watch_running = False

    def allow_draft76(self):
        return True

    def open(self):
        LiveReloadHandler.waiters.add(self)

    def on_close(self):
        LiveReloadHandler.waiters.remove(self)

    @classmethod
    def send_message(cls, message):
        if isinstance(message, dict):
            message = escape.json_encode(message)

        for waiter in cls.waiters:
            try:
                waiter.write_message(message)
            except:
                logging.error('Error sending message', exc_info=True)

    def watch_tasks(self):
        try:
            import julyfile
        except:
            Task.add(os.getcwd())

        path = Task.watch()
        if path:
            logging.info('Changed %s', path)
            msg = {
                'command': 'reload',
                'path': path,
                'liveCSS': True
            }
            self.send_message(msg)

    def on_message(self, message):
        logging.info(message)
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
            if not LiveReloadHandler._watch_running:
                LiveReloadHandler._watch_running = True
                logging.info('Start watching changes')
                tornado.ioloop.PeriodicCallback(self.watch_tasks, 500).start()


handlers = [
    (r'/livereload', LiveReloadHandler),
    (r'/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH}),
]


def main():
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=handlers)
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
