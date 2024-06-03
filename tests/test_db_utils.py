import os
import random
import string
import unittest
from pathlib import Path

from pykeepass.group import Group

from trapper_keeper.util.db_utils import DbUtils, SPECIAL_BINARIES
from pykeepass.pykeepass import PyKeePass

TEST_KEEPASS_DB_PATH: Path = Path('test_store.kdbx')
TEST_KEEPASS_DB_TOKEN: Path = Path('test_token')
TEST_PROP_DB_PATH: Path = Path('test_props.sqlite')


class TestKeepassCase(unittest.TestCase):

  def __init__(self, methodName: str = "runTest"):
    super().__init__(methodName)

  def setup_test_paths(self):
    """
    Sets up the paths for the test database and token files.
    """

    self.kp_token: Path = Path(f"test_resources/{TEST_KEEPASS_DB_TOKEN}")
    self.kp_path: Path = Path(f"test_resources/{TEST_KEEPASS_DB_PATH}")
    self.prop_path: Path = Path(f"./test_resources/{TEST_PROP_DB_PATH}")

  def setUp(self):
    """
    Sets up the test environment.
    """
    self.setup_test_paths()
    if self.kp_token.exists():
      os.remove(self.kp_token)
    if self.kp_path.exists():
      os.remove(self.kp_path)
    if self.prop_path.exists():
      os.remove(self.prop_path)
    with open("test_resources/test_token", "w") as f:
      f.write(''.join(random.choices(string.printable, k=20)))

  def test_create_tk_store(self):
    if not self.kp_path.exists():
      DbUtils.create_tk_store(kp_fp=self.kp_path, kp_token=self.kp_token, kp_key=None, kv_fp=self.prop_path)
    self.assertTrue(self.kp_token.exists())
    self.assertTrue(self.kp_path.exists())
    with (PyKeePass(filename=self.kp_path, password=self.kp_token.read_text(encoding='utf-8'))) as kp_db:
          group: Group = kp_db.find_groups(name=SPECIAL_BINARIES, first=True)
          self.assertIsNotNone(group)
          self.assertEqual(SPECIAL_BINARIES, group.name)
          self.assertGreater(len(group.entries), 0)
          self.assertGreater(len(kp_db.attachments), 0)

  def tearDown(self):
    """
    Tears down the test environment.
    """
    os.remove(self.kp_path)
    os.remove(self.kp_token)

if __name__ == '__main__':
  unittest.main()
