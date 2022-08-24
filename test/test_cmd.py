import unittest
from pathlib import Path
import sys

from port_env import command

BASE_DIR = Path(__file__).parent
TEST_FILES = BASE_DIR / "files"


class TestCmd(unittest.TestCase):
    def setUp(self):
        self.path = TEST_FILES

    def test_old_env(self):
        self.assertEqual(
            command._old_env(self.path / "bin" / "activate"),
            Path("/home/anon/bad/path/env"),
        )

    def test_fix_paths(self):
        res = command._fix_paths(
            r"/home/anon/bad/path/env",
            r"/home/anon/good/path/env",
            str(TEST_FILES / "bin"),
            _test=True,
        )

        self.assertIn("/home/anon/good/path/env", res[0])

    def test_site_packages(self):
        ver = "python" + ".".join(sys.version.split(".")[:2])
        self.assertEqual(command.fix_third_party(self.path, _test=True), self.path / "lib" / ver)
