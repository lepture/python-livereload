# -*- coding: utf-8 -*-
"""
    livereload.server
    ~~~~~~~~~~~~~~~~~

    WSGI app server for livereload.

    :copyright: (c) 2013 by Hsiaoming Yang
"""

from tornado import escape
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import Application, FallbackHandler
from .handlers import LiveReloadHandler, LiveReloadJSHandler, StaticHandler
from .watcher import Watcher


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
    def __init__(self, app=None, port=35729, root=None, watcher=None):
        self.app = app
        self.port = port
        self.root = root
        if not watcher:
            watcher = Watcher()
        self.watcher = watcher

        handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler, dict(port=port)),
        ]
        if app:
            app = WSGIWrapper(app)
            handlers.append(
                (r'.*', FallbackHandler, dict(fallback=app))
            )
        else:
            handlers.append(
                (r'(.*)', StaticHandler, dict(root=root)),
            )

        self.app = Application(handlers=handlers, debug=True)
        self.port = port

    def serve(self, port=None):
        if port:
            self.port = port

        self.app.listen(self.port)
        print('Serving on 127.0.0.1:%s' % self.port)
        try:
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print('Shutting down...')
