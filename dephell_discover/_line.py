import ast
from pathlib import Path
import sys
from typing import Optional

import attr

from ._constants import DOCSTRING


def _get_str(node) -> Optional[str]:
    if type(node) is ast.Str:
        return node.s
    if sys.version_info[:2] >= (3, 8):
        if type(node) is getattr(ast.Constant):
            return node.value
    return None


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
        if type(tree) is not ast.Module:
            return None
        # check is assigment
        if not tree.body or type(tree.body[0]) is not ast.Assign:  # type: ignore
            return None
        # check is correct target
        target = tree.body[0].targets[0]  # type: ignore
        if type(target) is not ast.Name:
            return None
        if target.id not in cls._vars:
            return None

        expr = tree.body[0].value  # type: ignore

        # get string
        value = _get_str(expr)
        if value:
            return cls(
                target=target.id,
                value=value,
                content=content,
                row=row,
                path=path,
            )

        # get list
        if type(expr) is ast.List or type(expr) is ast.Tuple:
            elements = [_get_str(element) for element in expr.elts]
            for element in elements:
                if element is None:
                    return None
            return cls(
                target=target.id,
                value=elements,
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
