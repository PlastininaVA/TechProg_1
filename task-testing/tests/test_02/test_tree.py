import os
import shutil

import pytest
from tree_utils_02.node import FileNode
from tree_utils_02.tree import Tree


@pytest.mark.parametrize(
    "path,is_dir,filename",
    [
        ("./file.txt", False, "file.txt"),
        ("./dir", True, "dir"),
        ("../dir", True, "dir"),
        ("/home/user/dir/file.txt", False, "file.txt"),
    ],
)
def test_construct(path: str, is_dir: bool, filename: str):
    node = Tree().construct_filenode(path, is_dir)
    assert node == FileNode(name=filename, is_dir=is_dir, children=[])


def test_update():
    node = FileNode(name="file.txt", is_dir=False, children=[FileNode("sub", True, [])])
    new_node = Tree().update_filenode(node)
    assert new_node == node


TMP_FOLDER = "./tests/test_02/tmp"


@pytest.fixture(scope="session", autouse=True)
def make_tree():
    os.mkdir(TMP_FOLDER)
    os.mkdir(f"{TMP_FOLDER}/empty")
    os.mkdir(f"{TMP_FOLDER}/nonempty")
    os.mkdir(f"{TMP_FOLDER}/nonempty/empty")
    os.mknod(f"{TMP_FOLDER}/nonempty/file.txt")
    yield
    shutil.rmtree(TMP_FOLDER)


def test_only_dirs():
    tree = Tree()
    node = tree.get(TMP_FOLDER, True)
    emptyNode = FileNode(name="empty", is_dir=True, children=[])
    assert node == FileNode(
        name=os.path.basename(TMP_FOLDER),
        is_dir=True,
        children=[
            emptyNode,
            FileNode(
                name="nonempty",
                is_dir=True,
                children=[emptyNode],
            ),
        ],
    )


def test_filter():
    tree = Tree()
    node = tree.get(TMP_FOLDER, False, True)
    tree.filter_empty_nodes(node, TMP_FOLDER)
    assert os.path.exists(f"{TMP_FOLDER}/nonempty")
    assert not os.path.exists(f"{TMP_FOLDER}/empty")
    assert not os.path.exists(f"{TMP_FOLDER}/nonempty/empty")
    assert os.path.exists(f"{TMP_FOLDER}/nonempty/file.txt")


def test_invalid_args():
    tree = Tree()

    with pytest.raises(AttributeError) as e:
        tree.get("/does/not/exists", False)
    assert str(e.value) == "Path not exist"

    assert tree.get(f"{TMP_FOLDER}/nonempty/file.txt", True, True) is None
    with pytest.raises(AttributeError) as e:
        tree.get(f"{TMP_FOLDER}/nonempty/file.txt", True)
    assert str(e.value) == "Path is not directory"
