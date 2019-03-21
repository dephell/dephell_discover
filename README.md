# Dephell Discover

Find project modules and data files (`packages` and `package_data` for `setup.py`).

## Installation

install from [PyPI](https://pypi.org/project/dephell-discover/):

```bash
python3 -m pip install --user dephell_discover
```

## Usage

```python
from pathlib import Path
from dephell_discover import Root

root = Root(path=Path('../dephell'))

# get packages:
root.packages
# [Package(path=Path('../dephell/dephell'), root=Path('../dephell')), ...]

# get package data:
root.data
# {Data(path=Path('../dephell/dephell/templates'), ext='.j2', package=Package(...)), ...}

# package properies:
p = root.packages[-1]
p.path    # Path('../dephell/dephell/commands')
p.root    # Path('../dephell')
p.module  # 'dephell.commands'
str(p)    # 'dephell.commands'
list(p)   # [Path('../dephell/dephell/commands/base.py'), ...]

# data properties:
d = next(iter(root.data))
d.path      # Path('../dephell/dephell/templates')
d.ext       # .j2
d.package   # Package(path=Path('../dephell/dephell'), root=...)
d.module    # 'dephell'
# relative path from package root:
d.relative  # 'templates/*.j2'
str(d)      # 'templates/*.j2'
list(d)     # [Path('../dephell/dephell/templates/python.html.j2'), ...]
```
