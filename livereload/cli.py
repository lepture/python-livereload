#!/usr/bin/env python

from docopt import docopt
from livereload import server


cmd = """Python LiveReload

Usage:
    livereload [-p <port>|--port=<port>] [-d <directory>|--directory=<directory>]

Options:
    -h --help                       show this screen
    -p <port> --port=<port>         specify a server port, default is 35729
    -d <root> --directory=<root>    specify a web root, default is '.'
"""


def main():
    args = docopt(cmd)
    port = args.get('--port')
    root = args.get('--directory')
    if port:
        port = int(port)
    else:
        port = 35729

    server.start(port, root)
