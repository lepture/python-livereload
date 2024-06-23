import click
from .server import Server
from .frameworks.sphinx import sphinx


@click.group(invoke_without_command=True)
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port. If 0, an available port will be picked.",
    show_default=True,
)
@click.pass_context
def main(
        ctx: click.Context,
        host: str,
        port: int,
) -> None:
    server = Server()
    server.config['host'] = host
    server.config['port'] = port
    ctx.ensure_object(dict)
    ctx.obj['server'] = server


# register framework commands
main.add_command(sphinx)
