import os
import shutil

import pytest
from tree_utils_02.size_node import FileSizeNode
from tree_utils_02.size_tree import SizeTree

TMP_FOLDER = "./tests/test_02/size"
FILE_PATH = f"{TMP_FOLDER}/file.txt"
FILE_SIZE = 420
BLOCK_SIZE = 4096


def make_file_with_size(path: str, size: int) -> None:
    assert size >= 0
    with open(path, "w") as f:
        f.write("\0" * size)


@pytest.fixture(scope="session", autouse=True)
def make_tree():
    os.mkdir(TMP_FOLDER)
    make_file_with_size(FILE_PATH, FILE_SIZE)
    yield
    shutil.rmtree(TMP_FOLDER)


def test_construct():
    tree = SizeTree()
    dir_node = tree.construct_filenode(TMP_FOLDER, True)
    assert dir_node == FileSizeNode(
        name=os.path.basename(TMP_FOLDER), is_dir=True, children=[], size=BLOCK_SIZE
    )
    file_node = tree.construct_filenode(FILE_PATH, False)
    assert file_node == FileSizeNode(
        name=os.path.basename(FILE_PATH), is_dir=False, children=[], size=FILE_SIZE
    )


def test_update():
    tree = SizeTree()
    dir_node = tree.construct_filenode(TMP_FOLDER, True)
    file_node = tree.construct_filenode(FILE_PATH, False)
    dir_node.children.append(file_node)
    new_node = tree.update_filenode(dir_node)
    assert new_node == FileSizeNode(
        name=os.path.basename(TMP_FOLDER),
        is_dir=True,
        children=[file_node],
        size=FILE_SIZE + BLOCK_SIZE,
    )
