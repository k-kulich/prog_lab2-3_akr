import os
import unittest
from unittest.mock import patch

import system_menu


class TestEnvironmentFunctions(unittest.TestCase):
    def test_get_environment_returns_dict(self):
        env = system_menu.get_environment()
        self.assertIsInstance(env, dict)
        self.assertIn("PATH", env)

    def test_set_and_unset_variable(self):
        name = "LAB_OS_TEST_VAR"
        system_menu.set_environment_variable(name, "hello")
        self.assertEqual(os.environ[name], "hello")
        self.assertTrue(system_menu.unset_environment_variable(name))
        self.assertNotIn(name, os.environ)

    def test_unset_missing_variable_returns_false(self):
        self.assertFalse(system_menu.unset_environment_variable("DEFINITELY_MISSING_VAR"))

    def test_set_invalid_name(self):
        with self.assertRaises(ValueError):
            system_menu.set_environment_variable("", "x")
        with self.assertRaises(ValueError):
            system_menu.set_environment_variable("A=B", "x")


class TestSystemInfo(unittest.TestCase):
    def test_system_info_contains_keys(self):
        info = system_menu.system_info()
        for key in ("os", "release", "version", "machine", "python", "cwd"):
            self.assertIn(key, info)

    def test_system_info_python_version(self):
        info = system_menu.system_info()
        self.assertRegex(info["python"], r"^\d+\.\d+")


class TestProcessFunctionsErrors(unittest.TestCase):
    def test_process_details_missing(self):
        with self.assertRaises(ProcessLookupError):
            system_menu.process_details(999_999_999)

    def test_kill_missing_process(self):
        with self.assertRaises(ProcessLookupError):
            system_menu.kill_process(999_999_999)

    def test_set_priority_invalid_value(self):
        with self.assertRaises(ValueError):
            system_menu.set_process_priority(1, "super-high")

    @patch("system_menu.psutil", None)
    def test_missing_psutil_raises(self):
        with self.assertRaises(RuntimeError):
            system_menu.list_processes()
        with self.assertRaises(RuntimeError):
            system_menu.process_details(1)
        with self.assertRaises(RuntimeError):
            system_menu.kill_process(1)
        with self.assertRaises(RuntimeError):
            system_menu.set_process_priority(1, "low")


class TestCurrentProcess(unittest.TestCase):
    def test_current_process_details(self):
        import os as _os
        pid = _os.getpid()
        details = system_menu.process_details(pid)
        self.assertEqual(details["pid"], pid)
        self.assertIn("name", details)
        self.assertIn("memory_mb", details)


class TestMenuExit(unittest.TestCase):
    def test_menu_exits_on_g(self):
        inputs = iter(["g"])
        output = []
        with patch("builtins.print", lambda *a, **k: output.append(" ".join(map(str, a)))):
            system_menu.run_menu(input_func=lambda prompt="": next(inputs))
        self.assertTrue(any("Выход" in line for line in output))

    def test_menu_unknown_option(self):
        inputs = iter(["z", "g"])
        output = []
        with patch("builtins.print", lambda *a, **k: output.append(" ".join(map(str, a)))):
            system_menu.run_menu(input_func=lambda prompt="": next(inputs))
        self.assertTrue(any("Неизвестная опция" in line for line in output))


if __name__ == "__main__":
    unittest.main()