import typing as t
import os
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.applications import Starlette
from starlette.datastructures import Headers, MutableHeaders
from starlette.routing import BaseRoute, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket
from starlette.middleware import Middleware
from .watcher import Watcher

ROOT = os.path.abspath(os.path.dirname(__file__))


class LivereloadClientMiddleware:
    INJECT_CODE = b'<script type="module" src="/@livereload/client.js"></script>'

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        initial_message: Message = {}
        should_inject: bool = False
        started: bool = False

        async def inject_livereload_client(message: Message) -> None:
            nonlocal should_inject
            nonlocal started
            nonlocal initial_message

            message_type = message["type"]
            if message_type == "http.response.start":
                initial_message = message
                headers = Headers(raw=message["headers"])
                content_type = headers.get('content-type')
                if content_type and content_type.startswith("text/html"):
                    should_inject = True
                else:
                    await send(message)
            elif message_type == "http.response.body" and should_inject and not started:
                started = True
                body = message.get("body", b"")
                index = body.find(b"<head>")
                if index != -1:
                    pos = index + 6
                    message["body"] = body[0:pos] + self.INJECT_CODE + body[pos:]

                    # alter initial_message header
                    headers = MutableHeaders(raw=initial_message["headers"])
                    content_length = int(headers["content-length"])
                    headers['content-length'] = str(content_length + len(self.INJECT_CODE))
                    if 'etag' in headers:
                        del headers['etag']
                    if 'last-modified' in headers:
                        del headers['last-modified']
                await send(initial_message)
                await send(message)
            else:
                await send(message)

        await self.app(scope, receive, inject_livereload_client)


class Server:
    config: t.Dict[str, t.Any] = {}

    def __init__(self, watcher: t.Optional[Watcher] = None) -> None:
        if watcher is None:
            watcher = Watcher()
        self.watcher = watcher
        self.routes: t.List[BaseRoute] = []

    def add_static_route(self, url: str = '/static', directory: str = 'static') -> None:
        self.routes.append(Mount(url, StaticFiles(directory=directory, follow_symlink=True), name='static'))

    def add_livereload_routes(self) -> None:
        async def websocket_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()
            self.watcher(websocket)

        self.routes.append(WebSocketRoute('/@livereload/ws', websocket_endpoint, name='livereload'))
        self.routes.append(Mount('/@livereload', StaticFiles(directory=os.path.join(ROOT, '_static'))))

    def add_app_route(self, app: ASGIApp) -> None:
        self.routes.append(Mount('/', app, name='app', middleware=[Middleware(LivereloadClientMiddleware)]))

    def prepare_routes(
            self,
            app: t.Optional[ASGIApp] = None,
            static_directory: t.Optional[str] = None,
            static_url: str = '/static',
        ) -> None:
        _has_routes: t.Dict[str, bool] = {}
        for route in self.routes:
            route_name = getattr(route, 'name', None)
            if route_name:
                _has_routes[route_name] = True

        if not _has_routes.get('livereload'):
            self.add_livereload_routes()

        if static_directory:
            self.add_static_route(static_url, static_directory)
        if app:
            self.add_app_route(app)

    def run(
            self,
            host: t.Optional[str] = None,
            port: t.Optional[int] = None,
        ) -> None:
        import uvicorn
        if host is None:
            host = self.config.get("host", "127.0.0.1")
        if port is None:
            port = self.config.get("port", 8000)
        uvicorn.run(
            Starlette(routes=self.routes),
            host=host,
            port=port,
        )
