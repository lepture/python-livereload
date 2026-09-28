import contextlib
import io
import unittest

from livereload.cli import parser
from livereload.server import (
    build_live_script,
    inject_script_at_head,
    normalize_base_path,
)


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


class TestNormalizeBasePath(unittest.TestCase):
    def test_empty_values_mean_no_base_path(self):
        for value in (None, '', '/', '//'):
            assert normalize_base_path(value) == ''

    def test_adds_leading_and_strips_trailing_slash(self):
        assert normalize_base_path('proxy/5500') == '/proxy/5500'
        assert normalize_base_path('/proxy/5500/') == '/proxy/5500'
        assert normalize_base_path('//a//') == '/a'

    def test_rejects_unsafe_characters(self):
        for value in ('/a"b', "/a'b", '/a<b', '/a b', '/a;b'):
            with self.assertRaises(ValueError):
                normalize_base_path(value)

    def test_rejects_query_and_fragment_characters(self):
        # These could add options to the livereload.js URL, e.g. &host=
        for value in ('/a?b', '/a&host=x', '/a=b', '/a#b'):
            with self.assertRaises(ValueError):
                normalize_base_path(value)

    def test_rejects_dot_segments(self):
        for value in ('/.', '/..', '/proxy/../5500', '/./proxy', '/a/..',
                      '/%2e%2e/x', '/%2E./x', '/.%2e'):
            with self.assertRaises(ValueError):
                normalize_base_path(value)

    def test_allows_dots_within_segments(self):
        assert normalize_base_path('/v1.2/...x/a..b') == '/v1.2/...x/a..b'

    def test_cannot_become_protocol_relative(self):
        # //evil.com in the script src would load it from another host
        assert normalize_base_path('//evil.com') == '/evil.com'


class TestBuildLiveScript(unittest.TestCase):
    def test_default_is_unchanged(self):
        expected = (
            b'<script type="text/javascript">(function(){'
            b'var s=document.createElement("script");'
            b"var port=(window.location.port || "
            b"(window.location.protocol == 'https:' ? 443: 80));"
            b's.src="//"+window.location.hostname+":"+port'
            b'+ "/livereload.js?port=" + port;'
            b'document.head.appendChild(s);'
            b'})();</script>'
        )
        assert build_live_script() == expected

    def test_liveport_is_unchanged(self):
        expected = (
            b'<script type="text/javascript">(function(){'
            b'var s=document.createElement("script");'
            b'var port=35729;'
            b's.src="//"+window.location.hostname+":"+port'
            b'+ "/livereload.js?port=" + port;'
            b'document.head.appendChild(s);'
            b'})();</script>'
        )
        assert build_live_script(35729) == expected

    def test_base_path_prefixes_script_and_websocket(self):
        script = build_live_script(base_path='/proxy/5500/')
        assert b'+ "/proxy/5500/livereload.js?port=" + port' in script
        assert b' + "&path=proxy/5500/livereload";' in script

    def test_rejects_unsafe_base_path(self):
        with self.assertRaises(ValueError):
            build_live_script(base_path='/"</script>')


class TestCliBasePath(unittest.TestCase):
    def test_defaults_to_none(self):
        assert parser.parse_args([]).base_path is None

    def test_accepts_and_normalizes_base_path(self):
        args = parser.parse_args(['--base-path', 'proxy/5500/'])
        assert args.base_path == '/proxy/5500'

    def test_invalid_base_path_is_a_usage_error(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args(['--base-path', '/a b'])
        assert cm.exception.code == 2
        assert "argument --base-path: invalid base path: '/a b'" in stderr.getvalue()

    def test_dot_segments_are_a_usage_error(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                parser.parse_args(['--base-path', '/proxy/../5500'])
        assert "'.' and '..' segments are not allowed" in stderr.getvalue()
