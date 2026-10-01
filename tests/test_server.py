import time
import unittest
from unittest.mock import patch

from livereload.server import Server, inject_script_at_head


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


class TestServerOpenUrl(unittest.TestCase):
    @patch('webbrowser.open')
    @patch('tornado.ioloop.IOLoop.instance')
    @patch('livereload.server.LiveReloadHandler.start_tasks')
    def test_open_url_true_opens_browser(self, mock_tasks, mock_ioloop, mock_browser):
        mock_ioloop.return_value.start.side_effect = lambda: None
        server = Server()
        server.serve(port=5500, open_url=True)
        time.sleep(0.05)
        mock_browser.assert_called_once_with('http://127.0.0.1:5500')
