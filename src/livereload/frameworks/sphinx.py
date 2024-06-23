import os
import shlex
import subprocess
import click
from starlette.routing import Mount
from ..server import Server
from .static import HTMLStaticFiles


@click.command
@click.option(
    "--source",
    type=str,
    help="Source directory of the documentation.",
)
@click.option(
    "--output",
    type=str,
    required=False,
    help="Output directory of the HTML.",
)
@click.option(
    "--builder",
    type=str,
    help="Sphinx builder to be used.",
    default="html",
    show_default=True,
)
@click.pass_context
def sphinx(ctx: click.Context, source: str, output: str, builder: str) -> None:
    server: Server = ctx.obj['server']
    server.config.update({
        'sphinx_source': source,
        'sphinx_output': output,
        'sphinx_builder': builder,
    })
    setup(server)
    server.run()


def setup(server: Server) -> None:
    source_dir = server.config.get('sphinx_source')
    output_dir = server.config.get('sphinx_output')
    builder = server.config.get('sphinx_builder', 'html')

    if not output_dir:
        # set a default output directory
        output_dir = 'build/_site'

    if not source_dir:
        source_dir = guess_docs_source_dir()

    # TODO: windows
    cmd = shlex.split(f'sphinx-build {source_dir} {output_dir} -b {builder}')
    if not os.path.isdir(output_dir):
        subprocess.run(cmd)

    server.add_livereload_routes()
    server.prepare_routes(
        app=HTMLStaticFiles(directory=output_dir, check_dir=False),
        static_url="/_static",
        static_directory=os.path.join(output_dir, '_static'),
    )


def guess_docs_source_dir() -> str:
    if os.path.isdir('docs'):
        root = 'docs'
    elif os.path.isdir('doc'):
        root = 'doc'
    else:
        # TODO
        raise

    if os.path.isfile(os.path.join(root, 'conf.py')):
        return root

    elif os.path.isfile(os.path.join(root, 'source/conf.py')):
        return os.path.join(root, 'source')

    # TODO
    raise
