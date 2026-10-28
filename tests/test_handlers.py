import asyncio
import json
from types import SimpleNamespace
from unittest import mock

from tornado import gen, httputil, web
from tornado.testing import AsyncHTTPTestCase, AsyncTestCase, gen_test
from tornado.websocket import WebSocketClosedError, websocket_connect

from livereload.handlers import LiveReloadHandler


class TestWebSocketWrites(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.previous_waiters = LiveReloadHandler.waiters
        LiveReloadHandler.waiters = set()
        request = httputil.HTTPServerRequest(
            start_line=httputil.RequestStartLine(
                'GET', '/livereload', 'HTTP/1.1'),
            headers=httputil.HTTPHeaders({'Host': 'localhost'}),
            connection=mock.Mock())
        self.handler = LiveReloadHandler(web.Application(), request)
        LiveReloadHandler.waiters.add(self.handler)

    def tearDown(self):
        LiveReloadHandler.waiters = self.previous_waiters
        super().tearDown()

    @gen_test
    async def test_delayed_disconnect_during_handshake(self):
        future = asyncio.Future()
        self.handler.write_message = mock.Mock(return_value=future)
        self.handler.send_message({'command': 'hello'})
        future.set_exception(WebSocketClosedError())
        await gen.sleep(0)
        await gen.sleep(0)
        try:
            self.assertNotIn(self.handler, LiveReloadHandler.waiters)
        finally:
            future.exception()

    @gen_test
    async def test_delayed_disconnect_during_reload(self):
        future = asyncio.Future()
        self.handler.write_message = mock.Mock(return_value=future)
        with mock.patch.object(LiveReloadHandler, 'watcher') as watcher:
            watcher.filepath = 'style.css'
            LiveReloadHandler.reload_waiters()
        future.set_exception(WebSocketClosedError())
        await gen.sleep(0)
        await gen.sleep(0)
        try:
            self.assertNotIn(self.handler, LiveReloadHandler.waiters)
        finally:
            future.exception()

    @gen_test
    async def test_successful_write_keeps_waiter(self):
        future = asyncio.Future()
        self.handler.write_message = mock.Mock(return_value=future)
        self.handler.send_message({'command': 'hello'})
        future.set_result(None)
        await gen.sleep(0)
        self.assertIn(self.handler, LiveReloadHandler.waiters)

    def test_immediate_disconnect_removes_waiter(self):
        self.handler.write_message = mock.Mock(
            side_effect=WebSocketClosedError())
        self.handler.send_message({'command': 'hello'})
        self.assertNotIn(self.handler, LiveReloadHandler.waiters)

    @gen_test
    async def test_unexpected_async_failure_is_logged(self):
        future = asyncio.Future()
        self.handler.write_message = mock.Mock(return_value=future)
        with mock.patch('livereload.handlers.logger.error') as log_error:
            self.handler.send_message({'command': 'hello'})
            future.set_exception(RuntimeError('write failed'))
            await gen.sleep(0)
            await gen.sleep(0)
            try:
                log_error.assert_called_once_with(
                    'Error sending message', exc_info=True)
            finally:
                future.exception()

    @gen_test
    async def test_cancelled_write_removes_waiter(self):
        future = asyncio.Future()
        self.handler.write_message = mock.Mock(return_value=future)
        self.handler.send_message({'command': 'hello'})
        future.cancel()
        await gen.sleep(0)
        await gen.sleep(0)
        self.assertNotIn(self.handler, LiveReloadHandler.waiters)


class TestLiveReloadWebSocket(AsyncHTTPTestCase):
    def get_app(self):
        return web.Application([(r'/livereload', LiveReloadHandler)])

    @gen_test
    async def test_handshake_and_reload(self):
        previous_waiters = LiveReloadHandler.waiters
        previous_watcher = LiveReloadHandler.watcher
        LiveReloadHandler.waiters = set()
        LiveReloadHandler.watcher = SimpleNamespace(filepath='style.css')
        socket = await websocket_connect(
            self.get_url('/livereload').replace('http:', 'ws:', 1))
        try:
            socket.write_message({'command': 'hello'})
            handshake = json.loads(await socket.read_message())
            self.assertEqual(handshake['command'], 'hello')
            socket.write_message({'command': 'info', 'url': 'http://localhost/'})
            # A second handshake acknowledges that the info frame was processed.
            socket.write_message({'command': 'hello'})
            await socket.read_message()
            self.assertEqual(len(LiveReloadHandler.waiters), 1)
            LiveReloadHandler.reload_waiters()
            message = json.loads(await socket.read_message())
            self.assertEqual(message['command'], 'reload')
            self.assertEqual(message['path'], 'style.css')
        finally:
            socket.close()
            LiveReloadHandler.waiters = previous_waiters
            LiveReloadHandler.watcher = previous_watcher
