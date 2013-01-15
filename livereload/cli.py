#!/usr/bin/env python

from docopt import docopt
from .server import start


cmd = """Python LiveReload

Usage:
    livereload [-p <port>|--port=<port>] [-b|--browser] [<directory>]

Options:
    -h --help                       show this screen
    -p <port> --port=<port>         specify a server port, default is 35729
    -b --browser                    open browser when start server
"""


def main():
    args = docopt(cmd)
    port = args.get('--port')
    root = args.get('<directory>')
    autoraise = args.get('--browser')
    if port:
        port = int(port)
    else:
        port = 35729

    start(port, root, autoraise)
