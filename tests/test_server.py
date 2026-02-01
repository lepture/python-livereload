import unittest

from livereload.server import inject_script_at_head


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
