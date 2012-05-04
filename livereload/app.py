import os
import logging
import tornado.web
import tornado.options
import tornado.ioloop
from tornado import escape
from tornado import websocket
from tornado.util import ObjectDict
from livereload.task import Task


ROOT = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(ROOT, 'static')


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
    def send_notify(cls, message):
        try:
            import gntp.notifier
            return gntp.notifier.mini(
                message, applicationName='Python LiveReload',
                title='LiveReload'
            )
        except ImportError:
            logging.info(message)

    def send_message(self, message):
        if isinstance(message, dict):
            message = escape.json_encode(message)

        try:
            self.write_message(message)
        except:
            logging.error('Error sending message', exc_info=True)

    def watch_tasks(self):

        path = Task.watch()
        if path:
            self.send_notify('Reload %s waiters\nChanged %s' % \
                             (len(self.waiters), path))
            msg = {
                'command': 'reload',
                'path': path,
                'liveCSS': True
            }
            for waiter in self.waiters:
                try:
                    waiter.write_message(msg)
                except:
                    logging.error('Error sending message', exc_info=True)

    def on_message(self, message):
        message = ObjectDict(escape.json_decode(message))
        if message.command == 'hello':
            if len(self.waiters) > 1:
                self.send_notify('Connect to %s pages' % len(self.waiters))

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
                try:
                    execfile('Guardfile')
                except:
                    Task.add(os.getcwd())

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
    app.listen(35729)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
