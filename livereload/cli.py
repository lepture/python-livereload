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
    help='Directory to watch for changes',
    type=str,
    default='.',
    nargs='?'
)
parser.add_argument(
    '-w', '--wait',
    help='Time delay in seconds before reloading',
    type=int,
    default=0
)
parser.add_argument(
    '-e', '--extension',
    help='Default extension for extensionless files',
    type=str,
    default=None,
)

def main(argv=None):
    args = parser.parse_args()

    # Create a new application
    server = Server()
    server.watcher.watch(args.directory, delay=args.wait)
    server.serve(host=args.host, port=args.port, root=args.directory, default_extension=args.extension)
