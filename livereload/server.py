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
from tornado import escape
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import Application, FallbackHandler
from .handlers import LiveReloadHandler, LiveReloadJSHandler, StaticHandler
from .watcher import Watcher
from ._compat import text_types
from tornado.log import enable_pretty_logging
enable_pretty_logging()


def shell(command, output=None, mode='w'):
    """Command shell command.

    You can add a shell command::

        server.watch('*.styl', shell('make stylus'))
    """
    if not output:
        output = os.devnull
    else:
        folder = os.path.dirname(output)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)

    cmd = command.split()

    def run_shell():
        try:
            p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
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
        code = stdout.decode()
        with open(output, mode) as f:
            f.write(code)

    return run_shell


class WSGIWrapper(WSGIContainer):
    """Insert livereload scripts into response body."""

    def __call__(self, request):
        data = {}
        response = []

        def start_response(status, response_headers, exc_info=None):
            data["status"] = status
            data["headers"] = response_headers
            return response.append
        app_response = self.wsgi_application(
            WSGIContainer.environ(request), start_response)
        try:
            response.extend(app_response)
            body = b"".join(response)
        finally:
            if hasattr(app_response, "close"):
                app_response.close()
        if not data:
            raise Exception("WSGI app did not call start_response")

        status_code = int(data["status"].split()[0])
        headers = data["headers"]
        header_set = set(k.lower() for (k, v) in headers)
        body = escape.utf8(body)
        if status_code != 304:
            if "content-length" not in header_set:
                headers.append(("Content-Length", str(len(body))))
            if "content-type" not in header_set:
                headers.append(("Content-Type", "text/html; charset=UTF-8"))
        if "server" not in header_set:
            headers.append(("Server", "livereload-tornado"))

        parts = [escape.utf8("HTTP/1.1 " + data["status"] + "\r\n")]
        for key, value in headers:
            parts.append(
                escape.utf8(key) + b": " + escape.utf8(value) + b"\r\n"
            )
        parts.append(b"\r\n")
        body = body.replace(
            '</head>',
            '<script src="/livereload.js"></script></head>'
        )
        parts.append(body)
        request.write(b"".join(parts))
        request.finish()
        self._log(status_code, request)


class Server(object):
    def __init__(self, app=None, port=5500, root=None, watcher=None):
        self.app = app
        self.port = port
        self.root = root
        if not watcher:
            watcher = Watcher()
        self.watcher = watcher

    def watch(self, filepath, func=None):
        """Add the given filepath for watcher list."""
        if isinstance(func, text_types):
            func = shell(func)

        self.watcher.watch(filepath, func)

    def application(self):
        LiveReloadHandler.watcher = self.watcher
        handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler, dict(port=self.port)),
        ]

        if self.app:
            self.app = WSGIWrapper(self.app)
            handlers.append(
                (r'.*', FallbackHandler, dict(fallback=self.app))
            )
        else:
            handlers.append(
                (r'(.*)', StaticHandler, dict(root=self.root or '.')),
            )
        return Application(handlers=handlers, debug=True)

    def serve(self, root=None, port=None):
        if root:
            self.root = root

        if port:
            self.port = port

        self.application().listen(self.port)
        logging.getLogger().setLevel(logging.INFO)
        print('Serving on 127.0.0.1:%s' % self.port)
        try:
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print('Shutting down...')
