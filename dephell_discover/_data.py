from pathlib import Path
from typing import Iterator

import attr

from ._relative import get_relative_path
from ._cached_propery import cached_property
from ._package import Package


@attr.s(hash=False)
class Data:
    path = attr.ib(type=Path)
    ext = attr.ib(type=str)
    package = attr.ib(type=Package)

    @property
    def module(self) -> str:
        return self.package.module

    @cached_property
    def relative(self) -> str:
        path = get_relative_path(path=self.path, root=self.package.path, sep='/')
        if path:
            return path + '/*' + self.ext
        return '*' + self.ext

    def __iter__(self) -> Iterator[Path]:
        yield from self.path.glob('*.py')

    def __str__(self) -> str:
        return self.relative

    def __hash__(self):
        return hash((self.path, self.ext))
