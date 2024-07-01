from __future__ import annotations
import typing as t
import os
from starlette.types import ASGIApp
from starlette.applications import Starlette
from starlette.routing import BaseRoute, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket
from starlette.middleware import Middleware
from .watcher import Watcher
from .middleware import LivereloadClientMiddleware

ROOT = os.path.abspath(os.path.dirname(__file__))


class Server:
    config: t.Dict[str, t.Any] = {}

    def __init__(self, watcher: Watcher | None = None) -> None:
        if watcher is None:
            watcher = Watcher()
        self.watcher = watcher

        async def websocket_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()
            watcher.connect(websocket)

        self.routes: list[BaseRoute] = [
            WebSocketRoute('/@livereload/ws', websocket_endpoint, name='livereload'),
            Mount('/@livereload', StaticFiles(directory=os.path.join(ROOT, '_static'))),
        ]

    def add_static_route(self, url: str = '/static', directory: str = 'static') -> None:
        self.routes.append(Mount(url, StaticFiles(directory=directory, follow_symlink=True), name='static'))
        # TODO: watch directory change

    def create_application(self, app: ASGIApp) -> Starlette:
        if isinstance(app, Starlette):
            app.add_middleware(LivereloadClientMiddleware)
            for route in self.routes:
                app.routes.append(route)
            return app

        self.routes.append(Mount('/', app, name='app', middleware=[Middleware(LivereloadClientMiddleware)]))
        return Starlette(routes=self.routes)

    def run(
            self,
            app: ASGIApp | None = None,
            host: str | None = None,
            port: int | None = None) -> None:
        import uvicorn
        if host is None:
            host = self.config.get("host", "127.0.0.1")
        if port is None:
            port = self.config.get("port", 8000)
        uvicorn.run(
            self.create_application(app),
            host=host,
            port=port,
        )
