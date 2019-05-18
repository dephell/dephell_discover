from pathlib import Path

import pytest

from dephell_discover._metainfo import MetaInfo


@pytest.mark.parametrize('content, name, expected', [
    ('__license__ = "MIT"', 'license', 'MIT'),

    ('__version__ = "0.2.7"', 'version', '0.2.7'),
    ('__version__ = ("0", "2", "7")', 'version', '0.2.7'),
    # ('__version__ = (0, 2, 7)', 'version', '0.2.7'),

    ('__author__ = "Gram"', 'authors', ['Gram']),
    ('__authors__ = ["Gram"]', 'authors', ['Gram']),

])
def test_vars(tmp_path: Path, content: str, name: str, expected):
    path = tmp_path / 'lol.py'
    path.write_text(content)
    info = MetaInfo.parse(paths=[path])
    assert getattr(info, name) == expected


def test_summary():
    path = Path('dephell_discover')
    info = MetaInfo.parse(paths=[path])
    assert info.summary == 'Discover python packages.'
