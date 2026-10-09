import os
import tempfile
import unittest

from files_demo import change_permissions, create_file, current_user, ensure_script_dir, file_exists, file_info, get_script_dir


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmpdir.cleanup()

    def test_create_file_and_check_exists(self):
        path = create_file("sample.txt", "hello")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(file_exists("sample.txt"))

    def test_create_file_writes_content(self):
        create_file("data.txt", "content-123")
        with open("data.txt", encoding="utf-8") as f:
            self.assertEqual(f.read(), "content-123")

    def test_file_info(self):
        create_file("info.txt", "abc")
        info = file_info("info.txt")
        self.assertTrue(info["exists"])
        self.assertEqual(info["size"], 3)
        self.assertIn("mtime", info)
        self.assertIn("atime", info)
        self.assertTrue(info["mode_octal"].startswith("0o"))

    def test_file_info_missing(self):
        info = file_info("nope.txt")
        self.assertFalse(info["exists"])

    def test_change_permissions(self):
        create_file("perm.txt", "x")
        result = change_permissions("perm.txt", 0o640)
        self.assertEqual(result, oct(0o640))

    def test_current_user_not_empty(self):
        user = current_user()
        self.assertIsInstance(user, str)
        self.assertTrue(len(user) > 0)

    def test_get_script_dir(self):
        d = get_script_dir()
        self.assertTrue(os.path.isdir(d))

    def test_ensure_script_dir_changes_cwd(self):
        before = os.getcwd()
        after = ensure_script_dir()
        self.assertNotEqual(before, after)
        self.assertEqual(after, get_script_dir())


if __name__ == "__main__":
    unittest.main()