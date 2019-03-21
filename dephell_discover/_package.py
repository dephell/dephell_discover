from pathlib import Path
from typing import Iterator

import attr

from ._relative import get_relative_path
from ._cached_propery import cached_property


@attr.s()
class Package:
    path = attr.ib(type=Path)
    root = attr.ib(type=Path)

    @cached_property
    def module(self) -> str:
        return get_relative_path(path=self.path, root=self.root)

    def __iter__(self) -> Iterator[Path]:
        yield from self.path.glob('*.py')

    def __str__(self) -> str:
        return self.module
