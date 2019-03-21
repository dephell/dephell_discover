from collections import defaultdict
from itertools import chain
from pathlib import Path
from posixpath import join as pjoin
from typing import List, Dict, Tuple

import attr

from ._relative import get_relative_path
from ._constants import BAD_DIRS_ANY, BAD_DIRS_ROOT
from ._cached_propery import cached_property
from ._package import Package


@attr.s()
class Root:
    path = attr.ib(type=Path)

    @property
    def name(self):
        return self.path.name

    def _find_nearest_pkg(self, path: Path) -> Tuple[str, str]:
        paths = {package.path for package in self.packages}
        for parent in chain((path,), path.parents):
            if parent in paths:
                pkg = get_relative_path(parent, root=self.path)
                rel_path = get_relative_path(path, root=parent, sep='/')
                return pkg, rel_path
        raise LookupError('cannot find package for data: ' + str(path))

    def include(self, path: Path) -> bool:
        parts = path.parts[len(self.path.parts):]
        # hidden dirs and files in root dir
        if parts[0][0] == '.':
            return False
        # bad dirs in the root of the project
        if parts[0] in BAD_DIRS_ROOT:
            return False
        # bad dirs inside the project
        if set(parts) & BAD_DIRS_ANY:
            return False
        return True

    @cached_property
    def packages(self) -> List[Package]:
        packages = []
        for path in self.path.glob('**/__init__.py'):
            if self.include(path=path):
                packages.append(Package(path=path.parent, root=self.path))
        return packages

    @cached_property
    def data(self) -> Dict[str, List[str]]:
        pkg_data = defaultdict(set)
        # Undocumented distutils feature: the empty string matches all package names
        pkg_data[''].add('*')

        for path in self.path.glob('**/*'):
            if not self.include(path=path):
                continue
            # skip dirs and python files
            if not path.is_file() or path.suffix == '.py':
                continue
            print(path)
            pkg, from_nearest_pkg = self._find_nearest_pkg(path=path.parent)
            pkg_data[pkg].add(pjoin(from_nearest_pkg, '*' + path.suffix))

        # Sort values in pkg_data
        pkg_data = {k: sorted(v) for k, v in pkg_data.items()}

        return pkg_data
