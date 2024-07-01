from starlette.websockets import WebSocket


class Watcher:
    websocket: WebSocket

    def connect(self, websocket: WebSocket) -> None:
        self.websocket = websocket
