import os
from collections import defaultdict
from pathlib import Path
from posixpath import join as pjoin
from typing import List

import attr


@attr.s()
class Package:
    path = attr.ib(type=Path)

    # https://github.com/takluyver/flit/blob/master/flit/sdist.py
    def _discover(self):
        """Discover subpackages and package_data"""
        pkgdir = os.path.normpath(str(self.path))
        pkg_name = os.path.basename(pkgdir)
        pkg_data = defaultdict(list)
        # Undocumented distutils feature: the empty string matches all package names
        pkg_data[''].append('*')
        packages = [pkg_name]
        subpkg_paths = set()

        def find_nearest_pkg(rel_path):
            parts = rel_path.split(os.sep)
            for i in reversed(range(1, len(parts))):
                ancestor = '/'.join(parts[:i])
                if ancestor in subpkg_paths:
                    pkg = '.'.join([pkg_name] + parts[:i])
                    return pkg, '/'.join(parts[i:])

            # Relative to the top-level package
            return pkg_name, rel_path

        for path, dirnames, filenames in os.walk(pkgdir, topdown=True):
            if os.path.basename(path) == '__pycache__':
                continue

            from_top_level = os.path.relpath(path, pkgdir)
            if from_top_level == '.':
                continue

            is_subpkg = '__init__.py' in filenames
            if is_subpkg:
                subpkg_paths.add(from_top_level)
                parts = from_top_level.split(os.sep)
                packages.append('.'.join([pkg_name] + parts))
            elif filenames:  # don't include empty dirs
                pkg, from_nearest_pkg = find_nearest_pkg(from_top_level)
                pkg_data[pkg].append(pjoin(from_nearest_pkg, '*'))

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
    def data(self):
        if 'data' in self.__dict__:
            return self.__dict__['data']
        self.__dict__['packages'], self.__dict__['data'] = self._discover()
        return self.__dict__['data']
