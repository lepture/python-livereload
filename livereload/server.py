"""
    livereload.server
    ~~~~~~~~~~~~~~~~~

    WSGI app server for livereload.

    :copyright: (c) 2013 - 2015 by Hsiaoming Yang
    :license: BSD, see LICENSE for more details.
"""

import os
import time
import shlex
import logging
import threading
import webbrowser
import re
from subprocess import Popen, PIPE
from urllib.parse import unquote

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.autoreload import add_reload_hook
from tornado import web
from tornado import escape
from tornado import httputil
from tornado.log import LogFormatter
from .handlers import LiveReloadHandler, LiveReloadJSHandler
from .handlers import ForceReloadHandler, StaticFileHandler
from .watcher import get_watcher_class

import sys

import errno

if sys.version_info >= (3, 8) and sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger('livereload')

HEAD_END_RE = re.compile(br'</head>', re.IGNORECASE)


def inject_script_at_head(content, script):
    """Inject script before closing </head> tag, case-insensitive."""
    return HEAD_END_RE.sub(lambda match: script + match.group(0), content, count=1)


BASE_PATH_RE = re.compile(r'^[A-Za-z0-9._~%/-]*$')


def normalize_base_path(base_path):
    """Normalize a URL base path to ``/prefix`` form, or ``''`` for none.

    The result is embedded in the injected script, so only characters that
    are safe in a URL path are allowed. ``.`` and ``..`` segments are
    rejected, as the browser would resolve them to a different path.
    """
    if not base_path:
        return ''
    if not BASE_PATH_RE.match(base_path):
        raise ValueError(
            f'invalid base path: {base_path!r} (allowed characters are '
            'letters, digits and . _ ~ % - /)'
        )
    stripped = base_path.strip('/')
    if any(unquote(segment) in ('.', '..') for segment in stripped.split('/')):
        raise ValueError(
            f"invalid base path: {base_path!r} ('.' and '..' segments are "
            'not allowed)'
        )
    return f'/{stripped}' if stripped else ''


def build_live_script(liveport=None, base_path=''):
    """Build the snippet that loads livereload.js into a page.

    Uses JavaScript to dynamically inject the client's hostname and, unless
    ``liveport`` is given, port. This allows for serving on 0.0.0.0 and
    behind a reverse proxy. ``base_path`` is the URL prefix of livereload as
    seen by the browser, and is passed on to livereload.js as its ``path``
    option so the websocket connects there too.
    """
    base_path = normalize_base_path(base_path)
    if liveport:
        port = liveport
    else:
        port = "(window.location.port || (window.location.protocol == 'https:' ? 443: 80))"
    options = ''
    if base_path:
        options = f' + "&path={base_path[1:]}/livereload"'
    live_script = (
        '<script type="text/javascript">(function(){'
        'var s=document.createElement("script");'
        f'var port={port};'
        's.src="//"+window.location.hostname+":"+port'
        f'+ "{base_path}/livereload.js?port=" + port{options};'
        'document.head.appendChild(s);'
        '})();</script>'
    )
    return escape.utf8(live_script)


def set_header(fn, name, value):
    """Helper Function to Add HTTP headers to the server"""
    def set_default_headers(self, *args, **kwargs):
        fn(self, *args, **kwargs)
        self.set_header(name, value)
    return set_default_headers


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
        cmd = shlex.split(cmd)

    def run_shell():
        try:
            p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd,
                      shell=shell)
        except OSError as e:
            logger.error(e)
            if e.errno == errno.ENOENT:  # file (command) not found
                logger.error("maybe you haven't installed %s", cmd[0])
            return e
        stdout, stderr = p.communicate()
        #: stdout is bytes, decode for python3
        stdout = stdout.decode()
        stderr = stderr.decode()
        if stderr:
            logger.error(stderr)
            return stderr
        with open(output, mode) as f:
            f.write(stdout)

    return run_shell


class LiveScriptInjector(web.OutputTransform):
    def __init__(self, request):
        super().__init__(request)

    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        is_html = "html" in headers.get("Content-Type", "")
        if is_html and HEAD_END_RE.search(chunk):
            chunk = inject_script_at_head(chunk, self.script)
            if 'Content-Length' in headers:
                length = int(headers['Content-Length']) + len(self.script)
                headers['Content-Length'] = str(length)
        return status_code, headers, chunk


class LiveScriptContainer(WSGIContainer):
    def __init__(self, wsgi_app, script=''):
        self.wsgi_app = wsgi_app
        self.script = script

    def __call__(self, request):
        data = {}
        response = []

        def start_response(status, response_headers, exc_info=None):
            data["status"] = status
            data["headers"] = response_headers
            return response.append

        app_response = self.wsgi_app(
            WSGIContainer(self.wsgi_app).environ(request), start_response)
        try:
            response.extend(app_response)
            body = b"".join(response)
        finally:
            if hasattr(app_response, "close"):
                app_response.close()
        if not data:
            raise Exception("WSGI app did not call start_response")

        status_code, reason = data["status"].split(' ', 1)
        status_code = int(status_code)
        headers = data["headers"]
        header_set = {k.lower() for (k, v) in headers}
        body = escape.utf8(body)

        if HEAD_END_RE.search(body):
            body = inject_script_at_head(body, self.script)

        if status_code != 304:
            if "content-type" not in header_set:
                headers.append((
                    "Content-Type",
                    "application/octet-stream; charset=UTF-8"
                ))
            if "content-length" not in header_set:
                headers.append(("Content-Length", str(len(body))))

        if "server" not in header_set:
            headers.append(("Server", "LiveServer"))

        start_line = httputil.ResponseStartLine(
            "HTTP/1.1", status_code, reason
        )
        header_obj = httputil.HTTPHeaders()
        for key, value in headers:
            if key.lower() == 'content-length':
                value = str(len(body))
            header_obj.add(key, value)
        request.connection.write_headers(start_line, header_obj, chunk=body)
        request.connection.finish()
        self._log(status_code, request)


class Server:
    """Livereload server interface.

    Initialize a server and watch file changes::

        server = Server(wsgi_app)
        server.serve()

    :param app: a WSGI application instance
    :param watcher: A Watcher instance, you don't have to initialize
                    it by yourself. Under Linux, you will want to install
                    pyinotify and use INotifyWatcher() to avoid wasted
                    CPU usage.
    """
    def __init__(self, app=None, watcher=None):
        self.root = None

        self.app = app
        if not watcher:
            watcher_cls = get_watcher_class()
            watcher = watcher_cls()
        self.watcher = watcher
        self.SFH = StaticFileHandler

    def setHeader(self, name, value):
        """Add or override HTTP headers at the at the beginning of the 
           request.

        Once you have initialized a server, you can add one or more 
        headers before starting the server::

            server.setHeader('Access-Control-Allow-Origin', '*')
            server.setHeader('Access-Control-Allow-Methods', '*')
            server.serve()

        :param name: The name of the header field to be defined.
        :param value: The value of the header field to be defined.
        """
        StaticFileHandler.set_default_headers = set_header(
                StaticFileHandler.set_default_headers, name, value)
        self.SFH = StaticFileHandler

    def watch(self, filepath, func=None, delay=None, ignore=None):
        """Add the given filepath for watcher list.

        Once you have initialized a server, watch file changes before
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
        :param delay: Delay sending the reload message. Use 'forever' to
                      not send it. This is useful to compile sass files to
                      css, but reload on changed css files then only.
        :param ignore: A function return True to ignore a certain pattern of
                       filepath.
        """
        if isinstance(func, str):
            cmd = func
            func = shell(func)
            func.name = f"shell: {cmd}"

        self.watcher.watch(filepath, func, delay, ignore=ignore)

    def application(self, port, host, liveport=None, debug=None,
                    live_css=True, base_path=''):
        LiveReloadHandler.watcher = self.watcher
        LiveReloadHandler.live_css = live_css
        if debug is None and self.app:
            debug = True

        live_handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/forcereload', ForceReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler)
        ]

        live_script = build_live_script(liveport, base_path)

        web_handlers = self.get_web_handlers(live_script)

        class ConfiguredTransform(LiveScriptInjector):
            script = live_script

        if not liveport:
            handlers = live_handlers + web_handlers
            app = web.Application(
                handlers=handlers,
                debug=debug,
                transforms=[ConfiguredTransform]
            )
            app.listen(port, address=host)
        else:
            app = web.Application(
                handlers=web_handlers,
                debug=debug,
                transforms=[ConfiguredTransform]
            )
            app.listen(port, address=host)
            live = web.Application(handlers=live_handlers, debug=False)
            live.listen(liveport, address=host)

    def get_web_handlers(self, script):
        if self.app:
            fallback = LiveScriptContainer(self.app, script)
            return [(r'.*', web.FallbackHandler, {'fallback': fallback})]
        return [
            (r'/(.*)', self.SFH, {
                'path': self.root or '.',
                'default_filename': self.default_filename,
            }),
        ]

    def serve(self, port=5500, liveport=None, host=None, root=None, debug=None,
              open_url=False, restart_delay=2, open_url_delay=None,
              live_css=True, default_filename='index.html', base_path=None):
        """Start serve the server with the given port.

        :param port: serve on this port, default is 5500
        :param liveport: live reload on this port
        :param host: serve on this hostname, default is 127.0.0.1
        :param root: serve static on this root directory
        :param debug: set debug mode, which autoreloads the app on code changes
                      via Tornado (and causes polling). Defaults to True when
                      ``self.app`` is set, otherwise False.
        :param open_url_delay: open webbrowser after the delay seconds
        :param live_css: whether to use live css or force reload on css.
                         Defaults to True
        :param default_filename: launch this file from the selected root on startup
        :param base_path: URL path prefix of livereload as seen by the
                          browser, e.g. ``/proxy/5500`` when behind a reverse
                          proxy that strips that prefix before forwarding.
                          With ``liveport``, this is the live server's prefix.
        """
        host = host or '127.0.0.1'
        if root is not None:
            self.root = root
        base_path = normalize_base_path(base_path)

        self._setup_logging()
        logger.info(f'Serving on http://{host}:{port}')
        if base_path:
            logger.info(f'Expecting to be proxied under {base_path}')

        self.default_filename = default_filename

        self.application(
            port, host, liveport=liveport, debug=debug, live_css=live_css,
            base_path=base_path)

        # Async open web browser after 5 sec timeout
        if open_url:
            logger.error('Use `open_url_delay` instead of `open_url`')
        if open_url_delay is not None:

            def opener():
                time.sleep(open_url_delay)
                webbrowser.open(f'http://{host}:{port}')
            threading.Thread(target=opener).start()

        try:
            self.watcher._changes.append(('__livereload__', restart_delay))
            LiveReloadHandler.start_tasks()
            # When autoreload is triggered, initiate a shutdown of the IOLoop
            add_reload_hook(lambda: IOLoop.instance().stop())
            # The call to start() does not return until the IOLoop is stopped.
            IOLoop.instance().start()
            # Once the IOLoop is stopped, the IOLoop can be closed to free resources
            IOLoop.current().close(all_fds=True)
        except KeyboardInterrupt:
            logger.info('Shutting down...')

    def _setup_logging(self):
        logger.setLevel(logging.INFO)

        channel = logging.StreamHandler()
        channel.setFormatter(LogFormatter())
        logger.addHandler(channel)

        # need a tornado logging handler to prevent IOLoop._setup_logging
        logging.getLogger('tornado').addHandler(channel)
