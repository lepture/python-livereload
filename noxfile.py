"""Development automation
"""
import os
import tempfile

import nox

PACKAGE_NAME = "livereload"
nox.options.sessions = ["test"]


#
# Helpers
#
def _install_this_project_with_flit(session, *, extras=None, editable=False):
    session.install("flit")
    args = []
    if extras:
        args.append("--extras")
        args.append(",".join(extras))
    if editable:
        args.append("--pth-file" if os.name == "nt" else "--symlink")

    session.run("flit", "install", "--deps=production", *args, silent=True)


#
# Development Sessions
#
@nox.session(name="docs-live", reuse_venv=True)
def docs_live(session):
    session.install("-r", "docs/requirements.txt")
    session.install("sphinx-autobuild")

    with tempfile.TemporaryDirectory() as destination:
        session.run(
            "sphinx-autobuild",
            # for sphinx-autobuild
            "--port=0",
            "--open-browser",
            # for sphinx
            "-b=dirhtml",
            "-a",
            "docs/",
            destination,
        )


@nox.session(reuse_venv=True)
def docs(session):
    _install_this_project_with_flit(session, editable=False)
    session.install("-r", "docs/requirements.txt")

    # Generate documentation into `build/docs`
    session.run("sphinx-build", "-b", "dirhtml", "-v", "docs/", "build/docs")


@nox.session(python=["3.6", "3.7", "3.8", "3.9", "3.10"])
def test(session):
    _install_this_project_with_flit(session)
    session.install("-r", "tests/requirements.txt")

    args = session.posargs or ["--cov", PACKAGE_NAME]
    session.run("pytest", *args)
