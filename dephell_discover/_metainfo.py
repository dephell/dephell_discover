from pathlib import Path
from typing import List, Optional

import attr

from ._cached_propery import cached_property
from ._line import Line


@attr.s()
class MetaInfo:
    lines = attr.ib(type=List[Line])

    _files = {
        '__init__.py',
        '__version__.py',
        '__about__.py',
        '_version.py',
        '_about.py',
    }

    @staticmethod
    def _parse_file(path: Path) -> List[Line]:
        lines = []
        with path.open('r', encoding='utf8') as stream:
            for row, content in enumerate(stream):
                line = Line.parse(content=content, row=row, path=path)
                if line is not None:
                    lines.append(line)
        return lines

    @staticmethod
    def parse(cls, paths: List[Path], recursive: bool = False) -> 'MetaInfo':
        lines = []
        for path in paths:
            # parse file
            if path.is_file():
                lines.extend(cls._parse_file(path=path))
                continue

            # parse files in dir
            pattern = '**/*.py' if recursive else '*.py'
            for subpath in path.glob(pattern):
                if subpath.name not in cls._files:
                    continue
                if not subpath.is_file():
                    continue
                lines.extend(cls._parse_file(path=subpath))

        return cls(lines=lines)

    def _get_var(self, name: str, sep: str = ', ') -> List[str]:
        for line in self.lines:
            if line.target == name:
                if type(line.value) is list:
                    return sep.join(line.value)
                return line.value
        return None

    @cached_property
    def authors(self) -> List[str]:
        authors = []
        for name in ('__author__', '__authors__', '__maintainer__', '__credits__'):
            var = self._get_var(name=name)
            if var:
                authors.extend(var.split(', '))
        if authors:
            for name in ('__email__', '__contact__'):
                if '<' in authors[0]:
                    continue
                mail = self._get_var(name=name)
                if mail:
                    authors[0] = '{} <{}>'.format(authors[0], mail)
        return authors

    @cached_property
    def license(self) -> Optional[str]:
        return self._get_var(name='__license__')

    @cached_property
    def version(self) -> List[str]:
        return self._get_var(name='__version__', sep='.')
