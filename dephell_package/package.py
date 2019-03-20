from collections import defaultdict
from pathlib import Path
from posixpath import join as pjoin
from typing import List, Dict, Tuple, Optional, Iterable

import attr


@attr.s()
class Package:
    path = attr.ib(type=Path)

    @property
    def name(self):
        return self.path.name

    def _convert(self, path: Path, root: Optional[Path] = None, sep: str = '.') -> str:
        if root is None:
            root = self.path
        parts = path.parts[len(root.parts):]
        if sep == '.':
            parts = (root.name, ) + parts
        return sep.join(parts)

    def _find_nearest_pkg(self, path: Path, subpkg_paths: Iterable[Path]) -> Tuple[str, str]:
        for parent in path.parents:
            if parent in subpkg_paths:
                pkg = self._convert(parent)
                rel_path = self._convert(path, root=parent, sep='/')
                return pkg, rel_path

        # Relative to the top-level package
        return self.name, '/'.join(path.parts[len(self.path.parts):])

    # https://github.com/takluyver/flit/blob/master/flit/sdist.py
    def _discover(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """Discover subpackages and package_data"""
        pkg_data = defaultdict(set)
        # Undocumented distutils feature: the empty string matches all package names
        pkg_data[''].add('*')
        packages = [self.name]
        subpkg_paths = set()

        for path in self.path.glob('**/*'):
            if '__pycache__' in path.parts:
                continue
            if path.parent.samefile(self.path):
                continue

            if path.name == '__init__.py':
                subpkg_paths.add(path.parent)
                packages.append(self._convert(path.parent))
            elif path.is_file():
                pkg, from_nearest_pkg = self._find_nearest_pkg(path=path.parent, subpkg_paths=subpkg_paths)
                pkg_data[pkg].add(pjoin(from_nearest_pkg, '*'))

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
