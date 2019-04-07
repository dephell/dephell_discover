from pathlib import Path
from typing import Iterator

import attr


@attr.s(slots=True)
class Package:
    path = attr.ib(type=Path)
    root = attr.ib(type=Path)
    module = attr.ib(type=str)

    @property
    def relative(self) -> str:
        path = self.path.relative_to(self.root).as_posix()
        if path == '.':
            return ''
        return path

    def __iter__(self) -> Iterator[Path]:
        yield from self.path.glob('*.py')

    def __str__(self) -> str:
        return self.module

    def __eq__(self, other):
        if not isinstance(other, Package):
            return NotImplemented
        return self.path == other.path
