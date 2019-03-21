from dephell_discover import Root


def test_discover_packages(tmp_path):
    p = Root(path=tmp_path)
    path = tmp_path / 'project1'

    path.mkdir()
    (path / 'dir1').mkdir()
    (path / 'dir2').mkdir()
    (path / 'dir3').mkdir()
    (path / 'dir3' / 'dir4').mkdir()
    (path / 'empty').mkdir()
    (path / '__pycache__').mkdir()

    (path / '__init__.py').touch()
    (path / 'file1.py').touch()
    (path / 'file2.db').touch()
    (path / 'dir1' / '__init__.py').touch()
    (path / 'dir2' / 'file3.json').touch()

    (path / 'dir3' / '__init__.py').touch()
    (path / 'dir3' / 'dir4' / 'file4.json').touch()

    (path / '__pycache__' / 'lol.pyc').touch()

    assert set(map(str, p.packages)) == {'project1', 'project1.dir1', 'project1.dir3'}
    assert set(p.data) == {'', 'project1', 'project1.dir3'}
    assert set(p.data['project1']) == {'*.db', 'dir2/*.json'}
    assert set(p.data['project1.dir3']) == {'dir4/*.json'}
