from collections import defaultdict
from pathlib import Path
from posixpath import join as pjoin
from typing import List, Dict, Tuple, Iterable

import attr

from ._relative import get_relative_path
from ._constants import BAD_DIRS_ANY, BAD_DIRS_ROOT


@attr.s()
class Root:
    path = attr.ib(type=Path)

    @property
    def name(self):
        return self.path.name

    def _find_nearest_pkg(self, path: Path, subpkg_paths: Iterable[Path]) -> Tuple[str, str]:
        for parent in path.parents:
            if parent in subpkg_paths:
                pkg = get_relative_path(parent, root=self.path)
                rel_path = get_relative_path(path, root=parent, sep='/')
                return pkg, rel_path
        if path in subpkg_paths:
            pkg = get_relative_path(path, root=self.path)
            return pkg, ''
        print(subpkg_paths)
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

    # https://github.com/takluyver/flit/blob/master/flit/sdist.py
    def _discover(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """Discover subpackages and package_data"""
        pkg_data = defaultdict(set)
        # Undocumented distutils feature: the empty string matches all package names
        pkg_data[''].add('*')
        packages = []
        subpkg_paths = set()

        for path in self.path.glob('**/__init__.py'):
            if not self.include(path=path):
                continue
            subpkg_paths.add(path.parent)
            packages.append(get_relative_path(path.parent, root=self.path))

        for path in self.path.glob('**/*'):
            if not self.include(path=path):
                continue
            # skip dirs and python files
            if not path.is_file() or path.suffix == '.py':
                continue
            print(path)
            pkg, from_nearest_pkg = self._find_nearest_pkg(path=path.parent, subpkg_paths=subpkg_paths)
            pkg_data[pkg].add(pjoin(from_nearest_pkg, '*' + path.suffix))

        # Sort values in pkg_data
        pkg_data = {k: sorted(v) for k, v in pkg_data.items()}

        return sorted(packages), pkg_data

    @property
    def packages(self) -> List[str]:
        if 'packages' in self.__dict__:
            return self.__dict__['packages']
        self.__dict__['packages'], self.__dict__['data'] = self._discover()
        return self.__dict__['packages']

    @property
    def data(self) -> Dict[str, List[str]]:
        if 'data' in self.__dict__:
            return self.__dict__['data']
        self.__dict__['packages'], self.__dict__['data'] = self._discover()
        return self.__dict__['data']
