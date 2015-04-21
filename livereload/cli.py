import argparse
from livereload.server import Server


parser = argparse.ArgumentParser(description='Start a `livereload` server')
parser.add_argument(
    '--host',
    help='Hostname to run `livereload` server on',
    type=str,
    default='127.0.0.1'
)
parser.add_argument(
    '-p', '--port',
    help='Port to run `livereload` server on',
    type=int,
    default=35729
)
parser.add_argument(
    'directory',
    help='Directories to watch for changes',
    type=str,
    nargs='*'
)


def main(argv=None):
    args = parser.parse_args()

    # Create a new application
    server = Server()
    if not args.directory:
        args.directory = ['.']
    for d in args.directory:
        server.watcher.watch(d)
    server.serve(host=args.host, port=args.port, root=args.directory)
