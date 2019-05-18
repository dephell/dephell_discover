import ast
from pathlib import Path
from typing import Optional

import attr

from ._constants import DOCSTRING


@attr.s(frozen=True)
class Line:
    target = attr.ib(type=str)
    value = attr.ib()
    content = attr.ib(type=str)

    row = attr.ib(type=int)
    path = attr.ib(type=Path)

    # https://stackoverflow.com/a/1523456/8704691
    _vars = {
        '__author__',
        '__authors__',
        '__contact__',
        '__copyright__',
        '__credits__',
        '__email__',
        '__homepage__',
        '__license__',
        '__maintainer__',
        '__version__',
    }

    @classmethod
    def parse(cls, content: str, row: int, path: Path) -> Optional['Line']:
        if '=' not in content:
            return None
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        # check is assigment
        if type(tree.body[0]) is not ast.Assign:
            return None
        # check is correct target
        target = tree.body[0].targets[0]
        if type(target) is not ast.Name:
            return None
        if target.id not in cls._vars:
            return None

        value = tree.body[0].value

        # get string
        if type(value) is ast.Str:
            return cls(
                target=target.id,
                value=value.s,
                content=content,
                row=row,
                path=path,
            )

        # get list
        if type(value) is ast.List or type(value) is ast.Tuple:
            for element in value.elts:
                if type(element) is not ast.Str:
                    return None
            return cls(
                target=target.id,
                value=[element.s for element in value.elts],
                content=content,
                row=row,
                path=path,
            )

        return None

    @classmethod
    def parse_docstring(cls, content: str, path: Path) -> Optional['Line']:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        docstring = ast.get_docstring(tree)
        if docstring is None:
            return None
        return cls(
            target=DOCSTRING,
            value=docstring,
            content='',
            row=0,
            path=path,
        )
