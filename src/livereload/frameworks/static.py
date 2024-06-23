from __future__ import annotations

import os
from starlette.staticfiles import StaticFiles


class HTMLStaticFiles(StaticFiles):
    def __init__(
            self,
            *,
            directory: str | None = None,
            packages: list[str | tuple[str, str]] | None = None,
            check_dir: bool = True,
    ) -> None:
        super().__init__(
            directory=directory,
            packages=packages,
            html=True,
            follow_symlink=True,
            check_dir=check_dir,
        )

    def lookup_path(self, path: str) -> tuple[str, os.stat_result | None]:
        full_path, stat_result = super().lookup_path(path)
        if stat_result is None and os.path.splitext(path)[1] == '':
            # retry with .html file
            return super().lookup_path(path + '.html')
        return full_path, stat_result
