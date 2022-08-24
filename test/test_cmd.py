import unittest
from pathlib import Path

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
            r"/home/anon/bad/path/env".replace("/", "\/"),
            r"/home/anon/good/path/env".replace("/", "\/"),
            str(TEST_FILES / "bin"),
            _test=True,
        )

        assert "/home/anon/good/path/env" in res[0]
