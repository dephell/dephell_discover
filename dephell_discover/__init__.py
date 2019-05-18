"""Discover python packages.

+ Find project modules and data files (packages and package_data for setup.py).
+ Extract metainfo.
"""

from ._data import Data
from ._package import Package
from ._root import Root


__version__ = '0.2.0'
__author__ = 'Gram (@orsinium)'
__license__ = 'MIT'


__all__ = [
    'Data',
    'Package',
    'Root',
]
