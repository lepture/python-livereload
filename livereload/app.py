# -*- coding: utf-8 -*-

"""livereload.app

Core Server of LiveReload.
"""

import os
import sys
import logging
import tornado.web
import tornado.options
import tornado.ioloop
from tornado import escape
from tornado import websocket
from tornado.util import ObjectDict
from livereload.task import Task


ROOT = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(ROOT, 'livereload-js/dist')

NOTIFIER = None
APPLICATION_ICON = None


def _get_growl():
    import gntp.notifier
    growl = gntp.notifier.GrowlNotifier(
        applicationName='Python LiveReload',
        notifications=['Message'],
        defaultNotifications=['Message'],
        applicationIcon=APPLICATION_ICON,
    )
    result = growl.register()
    if result is not True:
        return None

    def notifier(message):
        return growl.notify(
            'Message',
            'LiveReload',
            message,
            icon=APPLICATION_ICON,
        )

    return notifier


def _get_notifyOSD():
    import pynotify
    pynotify.init('Python LiveReload')
    return lambda message: pynotify.Notification('LiveReload', message).show()


def send_notify(message):
    global NOTIFIER
    if NOTIFIER:
        return NOTIFIER(message)
    try:
        NOTIFIER = _get_growl()
    except:
        try:
            NOTIFIER = _get_notifyOSD()
        except:
            NOTIFIER = logging.info

    return NOTIFIER(message)


class LiveReloadHandler(websocket.WebSocketHandler):
    waiters = set()
    _watch_running = False

    def allow_draft76(self):
        return True

    def on_close(self):
        if self in LiveReloadHandler.waiters:
            LiveReloadHandler.waiters.remove(self)
            #send_notify('There are %s waiters left' % len(self.waiters))

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
            send_notify(
                'Reload %s waiters'
                '\nChanged %s'
                % (len(LiveReloadHandler.waiters), path)
            )
            msg = {
                'command': 'reload',
                'path': path,
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
            send_notify('Browser Connected: %s' % message.url)
            LiveReloadHandler.waiters.add(self)
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
    (
        r'/(livereload.js)',
        tornado.web.StaticFileHandler,
        {'path': STATIC_PATH}
    ),
]


def main():
    if len(sys.argv) > 1:
        #: command-line tools like Makefile
        execfile('Guardfile')
        for cmd in sys.argv[1:]:
            print(cmd)
            exec('%s()' % cmd)
        return

    #: option config is not available
    #: but this enables pretty colorful logging
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=handlers)
    app.listen(35729)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
