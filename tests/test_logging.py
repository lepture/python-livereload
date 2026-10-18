import logging
import unittest
from unittest import mock

from tornado.log import LogFormatter

from livereload import cli
from livereload.server import Server


class TestServerLogging(unittest.TestCase):
    def setUp(self):
        self.loggers = [logging.getLogger(name) for name in ('livereload', 'tornado')]
        self.original = [(logger.level, logger.handlers[:]) for logger in self.loggers]
        for logger in self.loggers:
            logger.setLevel(logging.ERROR)
            logger.handlers = [logging.NullHandler()]

    def tearDown(self):
        for logger, (level, handlers) in zip(self.loggers, self.original):
            logger.setLevel(level)
            logger.handlers = handlers

    def test_library_serve_preserves_logging_configuration(self):
        server = Server()
        handlers = [logger.handlers[:] for logger in self.loggers]

        # Stop before opening sockets or entering the event loop, after the
        # point at which serve previously changed the caller's logging setup.
        with mock.patch.object(server, 'application', side_effect=RuntimeError('stop')):
            for _ in range(2):
                with self.assertRaisesRegex(RuntimeError, 'stop'):
                    server.serve()
                for logger, expected in zip(self.loggers, handlers):
                    self.assertEqual(logger.level, logging.ERROR)
                    self.assertEqual(logger.handlers, expected)

    def test_cli_still_configures_default_logging(self):
        server = Server()
        with mock.patch.object(cli, 'Server', return_value=server), \
                mock.patch.object(server, 'serve'), \
                mock.patch.object(server.watcher, 'watch'), \
                mock.patch('sys.argv', ['livereload']):
            cli.main()

        logger = self.loggers[0]
        self.assertEqual(logger.level, logging.INFO)
        channel = logger.handlers[-1]
        self.assertIsInstance(channel, logging.StreamHandler)
        self.assertIsInstance(channel.formatter, LogFormatter)
        self.assertIn(channel, self.loggers[1].handlers)
