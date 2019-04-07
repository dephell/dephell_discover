from pathlib import Path
from typing import Iterator

import attr

from ._cached_propery import cached_property
from ._package import Package


@attr.s(hash=False, slots=True)
class Data:
    path = attr.ib(type=Path)
    ext = attr.ib(type=str)
    package = attr.ib(type=Package)

    @property
    def module(self) -> str:
        return self.package.module

    @property
    def relative(self) -> str:
        path = self.path.relative_to(self.package.path).as_posix()
        if path == '.':
            return '*' + self.ext
        return path + '/*' + self.ext

    def __iter__(self) -> Iterator[Path]:
        yield from self.path.glob('*' + self.ext)

    def __str__(self) -> str:
        return self.relative

    def __hash__(self):
        return hash((self.path, self.ext))
