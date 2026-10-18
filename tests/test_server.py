import unittest

from tornado import httputil, web
from tornado.testing import AsyncHTTPTestCase

from livereload.server import LiveScriptInjector, inject_script_at_head


class TestInjectScriptAtHead(unittest.TestCase):
    def test_injects_before_mixed_case_head_end(self):
        content = b"<html><HeAd><title>x</title></HeAd></html>"
        script = b"<script>LR</script>"
        expected = (
            b"<html><HeAd><title>x</title>"
            + script
            + b"</HeAd></html>"
        )
        assert inject_script_at_head(content, script) == expected

    def test_injects_only_first_head_end(self):
        content = b"<head></head><head></head>"
        script = b"<script>LR</script>"
        expected = b"<head>" + script + b"</head><head></head>"
        assert inject_script_at_head(content, script) == expected

    def test_no_head_end_returns_original(self):
        content = b"<html><body>no head end</body></html>"
        script = b"<script>LR</script>"
        assert inject_script_at_head(content, script) == content


class TestLiveScriptInjector(unittest.TestCase):
    script = b'<script>LR</script>'

    def transform(self, chunks, content_type='text/html', method='GET'):
        request = httputil.HTTPServerRequest(method=method)
        transform = LiveScriptInjector(request)
        transform.script = self.script
        headers = httputil.HTTPHeaders({
            'Content-Type': content_type,
            'Content-Length': str(sum(map(len, chunks))),
        })
        _, headers, first = transform.transform_first_chunk(
            200, headers, chunks[0], len(chunks) == 1)
        output = [first]
        for index, chunk in enumerate(chunks[1:], 1):
            output.append(transform.transform_chunk(
                chunk, index == len(chunks) - 1))
        return headers, b''.join(output)

    def test_injects_in_later_chunk(self):
        chunks = [b'<head>' + b'x' * 65536, b'</HeAd><body>page</body>']
        headers, body = self.transform(chunks)
        self.assertEqual(body, inject_script_at_head(b''.join(chunks), self.script))
        self.assertNotIn('Content-Length', headers)

    def test_head_end_at_every_chunk_boundary(self):
        for split in range(1, len(b'</head>')):
            with self.subTest(split=split):
                chunks = [b'<head>' + b'</HeAd>'[:split],
                          b'</HeAd>'[split:] + b'<body>page</body>']
                _, body = self.transform(chunks)
                self.assertEqual(body, inject_script_at_head(b''.join(chunks), self.script))

    def test_one_byte_chunks(self):
        content = b'<head></head><head></head>'
        _, body = self.transform([content[i:i + 1] for i in range(len(content))])
        self.assertEqual(body, inject_script_at_head(content, self.script))

    def test_injects_only_once_across_chunks(self):
        for chunks in ([b'<head></head>', b'<head></head>'],
                       [b'<head>', b'</head>', b'<head></head>']):
            with self.subTest(chunks=chunks):
                _, body = self.transform(chunks)
                self.assertEqual(body, inject_script_at_head(b''.join(chunks), self.script))

    def test_no_closing_head_preserves_all_bytes(self):
        chunks = [b'<head>', b'abc', b'd']
        _, body = self.transform(chunks)
        self.assertEqual(body, b''.join(chunks))

    def test_non_html_is_unchanged(self):
        chunks = [b'<head>', b'</head>']
        headers, body = self.transform(chunks, content_type='text/plain')
        self.assertEqual(body, b''.join(chunks))
        self.assertEqual(headers['Content-Length'], str(len(body)))

    def test_complete_response_keeps_correct_length(self):
        headers, body = self.transform([b'<head></head>'])
        self.assertEqual(body, b'<head>' + self.script + b'</head>')
        self.assertEqual(int(headers['Content-Length']), len(body))

    def test_head_request_does_not_start_streaming_injection(self):
        headers, body = self.transform([b'', b''], method='HEAD')
        self.assertEqual(headers['Content-Length'], '0')
        self.assertEqual(body, b'')


class TestStreamingInjection(AsyncHTTPTestCase):
    content = b'<head>' + b'x' * 65536 + b'</head><body>page</body>'
    script = b'<script>LR</script>'

    def get_app(self):
        content = self.content

        class Handler(web.RequestHandler):
            async def get(self):
                self.set_header('Content-Type', 'text/html')
                self.set_header('Content-Length', len(content))
                self.write(content[:65536])
                await self.flush()
                self.write(content[65536:])

        class Transform(LiveScriptInjector):
            script = self.script

        return web.Application([(r'/', Handler)], transforms=[Transform])

    def test_http_response_is_complete_and_injected(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, inject_script_at_head(self.content, self.script))
