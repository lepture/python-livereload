# -*- coding: utf-8 -*-
"""
    livereload.server
    ~~~~~~~~~~~~~~~~~

    WSGI app server for livereload.

    :copyright: (c) 2013 by Hsiaoming Yang
"""

import os
import logging
from subprocess import Popen, PIPE
import time
import threading
import webbrowser

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado import web
from .handlers import LiveReloadHandler, LiveReloadJSHandler
from .handlers import ForceReloadHandler
from .watcher import Watcher
from ._compat import text_types, PY3
from tornado.log import enable_pretty_logging
enable_pretty_logging()

HEAD_END = b'</head>'


def shell(cmd, output=None, mode='w', cwd=None, shell=False):
    """Execute a shell command.

    You can add a shell command::

        server.watch(
            'style.less', shell('lessc style.less', output='style.css')
        )

    :param cmd: a shell command, string or list
    :param output: output stdout to the given file
    :param mode: only works with output, mode ``w`` means write,
                 mode ``a`` means append
    :param cwd: set working directory before command is executed.
    :param shell: if true, on Unix the executable argument specifies a
                  replacement shell for the default ``/bin/sh``.
    """
    if not output:
        output = os.devnull
    else:
        folder = os.path.dirname(output)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)

    if not isinstance(cmd, (list, tuple)) and not shell:
        cmd = cmd.split()

    def run_shell():
        try:
            p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd,
                      shell=shell)
        except OSError as e:
            logging.error(e)
            if e.errno == os.errno.ENOENT:  # file (command) not found
                logging.error("maybe you haven't installed %s", cmd[0])
            return e
        stdout, stderr = p.communicate()
        if stderr:
            logging.error(stderr)
            return stderr
        #: stdout is bytes, decode for python3
        if PY3:
            stdout = stdout.decode()
        with open(output, mode) as f:
            f.write(stdout)

    return run_shell


class LiveScriptInjector(web.OutputTransform):
    def __init__(self, request):
        super(LiveScriptInjector, self).__init__(request)

    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        if HEAD_END in chunk:
            chunk = chunk.replace(HEAD_END, self.script + HEAD_END)
            if 'Content-Length' in headers:
                headers['Content-Length'] = str(
                    int(headers['Content-Length']) + len(self.script))
        return status_code, headers, chunk


class BaseServer(object):
    """Livreload server base class

    subclass and override get_web_handlers
    """
    def __init__(self, watcher=None):
        self.root = None
        if not watcher:
            watcher = Watcher()
        self.watcher = watcher

    def watch(self, filepath, func=None, delay=None):
        """Add the given filepath for watcher list.

        Once you have intialized a server, watch file changes before
        serve the server::

            server.watch('static/*.stylus', 'make static')
            def alert():
                print('foo')
            server.watch('foo.txt', alert)
            server.serve()

        :param filepath: files to be watched, it can be a filepath,
                         a directory, or a glob pattern
        :param func: the function to be called, it can be a string of
                     shell command, or any callable object without
                     parameters
        :param delay: delay a certain seconds to send the reload message
        """
        if isinstance(func, text_types):
            func = shell(func)

        self.watcher.watch(filepath, func, delay)

    def application(self, port, host, liveport=None, debug=True):
        LiveReloadHandler.watcher = self.watcher
        if liveport is None:
            liveport = port

        live_handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/forcereload', ForceReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler)
        ]
        web_handlers = self.get_web_handlers()

        class ConfiguredTransform(LiveScriptInjector):
            script = (
                '<script src="http://{host}:{port}/livereload.js"></script>'
            ).format(host=host, port=liveport).encode('ascii')

        if liveport == port:
            handlers = live_handlers + web_handlers
            app = web.Application(handlers=handlers, debug=debug)
            app.add_transform(ConfiguredTransform)
            app.listen(port, address=host)
        else:
            app = web.Application(handlers=web_handlers, debug=debug)
            app.add_transform(ConfiguredTransform)
            app.listen(port, address=host)
            live = web.Application(handlers=live_handlers, debug=False)
            live.listen(liveport, address=host)

    def serve(self, port=5500, liveport=None, host=None, root=None, debug=True,
              open_url=False, restart_delay=2):
        """Start serve the server with the given port.

        :param port: serve on this port, default is 5500
        :param liveport: live reload on this port
        :param host: serve on this hostname, default is 0.0.0.0
        :param root: serve static on this root directory
        :param open_url: open system browser
        """
        host = host or '0.0.0.0'
        if root is not None:
            self.root = root

        self.application(port, host, liveport=liveport, debug=debug)
        logging.getLogger().setLevel(logging.INFO)

        print('Serving on http://%s:%s' % (host, port))

        # Async open web browser after 5 sec timeout
        if open_url:
            def opener():
                time.sleep(5)
                webbrowser.open('http://%s:%s' % (host, port))
            threading.Thread(target=opener).start()

        try:
            self.watcher._changes.append(('__livereload__', restart_delay))
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print('Shutting down...')

    def get_web_handlers(self):
        raise NotImplementedError


class Server(BaseServer):
    """Livereload server interface.

    Initialize a server and watch file changes::

        server = Server(wsgi_app)
        server.serve()

    :param app: a wsgi application instance
    :param watcher: A Watcher instance, you don't have to initialize
                    it by yourself. Under Linux, you will want to install
                    pyinotify and use INotifyWatcher() to avoid wasted
                    CPU usage.
    """
    def __init__(self, app=None, watcher=None):
        self.app = app
        super(Server, self).__init__(watcher=watcher)

    def get_web_handlers(self):

        if self.app:
            return [
                (r'.*', web.FallbackHandler, {
                    'fallback': WSGIContainer(self.app)})
            ]
        else:
            return [
                (r'/(.*)', web.StaticFileHandler, {
                    'path': self.root or '.',
                    'default_filename': 'index.html',
                }),
            ]
