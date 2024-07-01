from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.datastructures import Headers, MutableHeaders


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
