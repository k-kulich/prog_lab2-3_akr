import os
import tempfile
import unittest

from dirs_demo import copy_file, create_and_remove_empty_dir, create_files, list_dir, make_dirs, move_file, rename_file, walk_tree


class TestDirectoryOperations(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmpdir.cleanup()

    def test_copy_file(self):
        copy_file("src.txt", "dst.txt")
        self.assertTrue(os.path.exists("src.txt"))
        self.assertTrue(os.path.exists("dst.txt"))

    def test_rename_file(self):
        create_files(["a.txt"])
        rename_file("a.txt", "b.txt")
        self.assertFalse(os.path.exists("a.txt"))
        self.assertTrue(os.path.exists("b.txt"))

    def test_make_dirs(self):
        make_dirs(["x", "x/y", "x/y/z"])
        self.assertTrue(os.path.isdir("x/y/z"))

    def test_move_file(self):
        create_files(["m.txt"])
        os.makedirs("target", exist_ok=True)
        move_file("m.txt", "target/m.txt")
        self.assertTrue(os.path.exists("target/m.txt"))
        self.assertFalse(os.path.exists("m.txt"))

    def test_create_files_and_list_dir(self):
        create_files(["f1.txt", "f2.txt"])
        os.makedirs("subdir", exist_ok=True)
        listing = list_dir(".")
        self.assertIn("f1.txt", listing["files"])
        self.assertIn("f2.txt", listing["files"])
        self.assertIn("subdir", listing["dirs"])

    def test_walk_tree(self):
        make_dirs(["a/b"])
        create_files(["a/b/file.txt"])
        tree = walk_tree(".")
        paths = [entry["path"] for entry in tree]
        self.assertTrue(any("a" in p for p in paths))
        file_entries = [e for e in tree if "file.txt" in e["files"]]
        self.assertTrue(file_entries)

    def test_create_and_remove_empty_dir(self):
        result = create_and_remove_empty_dir("tmp_empty")
        self.assertTrue(result)
        self.assertFalse(os.path.exists("tmp_empty"))


if __name__ == "__main__":
    unittest.main()