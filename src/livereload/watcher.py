from starlette.websockets import WebSocket


class Watcher:
    websocket: WebSocket

    def __init__(self, root: str = '.') -> None:
        self.root = root

    def __call__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
