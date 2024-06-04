import os
import random
import string
import unittest
from pathlib import Path

from boltdb import BoltDB
from boltdb.tx import Tx
from boltdb.bucket import Bucket
from boltdb.page import Page
from pykeepass.group import Group
from pykeepass.pykeepass import PyKeePass

from trapper_keeper.util.db_utils import DbUtils, SPECIAL_BINARIES

TEST_KEEPASS_DB_PATH: Path = Path('test_store.kdbx')
TEST_KEEPASS_DB_TOKEN: Path = Path('test_token')
TEST_KEEPASS_DB_KEY: Path = Path('test_key')
TEST_BOLT_DB_PATH: Path = Path('chezmoistate.boltdb')
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
    self.bp_path: Path = Path(f"test_resources/{TEST_BOLT_DB_PATH}")
    self.kp_key: Path = Path(f"test_resources/{TEST_KEEPASS_DB_KEY}")
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
    if self.bp_path.exists():
      os.remove(self.bp_path)
    if self.kp_key.exists():
      os.remove(self.kp_key)
    with open("test_resources/test_token", "w") as f:
      f.write(''.join(random.choices(string.printable, k=35)))
    with open("test_resources/test_key", "w") as f:
      f.write(''.join(random.choices(string.printable, k=180)))

  def test_create_tk_store(self):
    if not self.kp_path.exists():
      DbUtils.create_tk_store(kp_fp=self.kp_path, kp_token=self.kp_token, kp_key=self.kp_key, kv_fp=self.prop_path)
    self.assertTrue(self.kp_token.exists())
    self.assertTrue(self.kp_path.exists())
    with (PyKeePass(filename=self.kp_path, password=self.kp_token.read_text(encoding='utf-8'),
                    keyfile=self.kp_key)) as kp_db:
      group: Group = kp_db.find_groups(name=SPECIAL_BINARIES, first=True)
      self.assertIsNotNone(group)
      self.assertEqual(SPECIAL_BINARIES, group.name)
      self.assertGreater(len(group.entries), 0)
      self.assertGreater(len(kp_db.attachments), 0)

  def test_chezmoi_bolt_db_rw(self):
    db: BoltDB = BoltDB(filename=self.bp_path)
    tx: Tx = db.begin(writable=True)
    config_state = tx.create_bucket(b"configState")
    config_state.put(b"configState", b"1")
    tx.entry_state = tx.create_bucket(b"entryState")
    tx.git_external = tx.create_bucket(b"gitRepoExternalState")
    tx.git_hub_keys = tx.create_bucket(b"gitHubKeysState")
    tx.git_hub_latest_release = tx.create_bucket(b"gitHubLatestReleaseState")
    tx.git_hub_tags = tx.create_bucket(b"gitHubTagsState")
    tx.script_state = tx.create_bucket(b"scriptState")
    tx.write()
    tx.commit()
    tx.close()


    bolt_db: BoltDB = DbUtils.load_boltdb_store(self.bp_path)
    self.assertIsNotNone(bolt_db)
    tx: Tx = bolt_db.begin(writable=False)
    self.assertIsNotNone(tx)
    config_state = tx.bucket(b"configState")
    self.assertIsNotNone(config_state)
    config_state_val = config_state.get(b"configState")
    self.assertIsNotNone(config_state_val)
    entry_state = tx.bucket(b"entryState")
    self.assertIsNotNone(entry_state)
    github_keys = tx.bucket(b"gitHubKeysState")
    self.assertIsNotNone(github_keys)
    github_release = tx.bucket(b"gitHubLatestReleaseState")
    self.assertIsNotNone(github_release)
    github_tags = tx.bucket(b"gitHubTagsState")
    self.assertIsNotNone(github_tags)
    git_external = tx.bucket(b"gitRepoExternalState")
    self.assertIsNotNone(git_external)
    script_state = tx.bucket(b"scriptState")
    self.assertIsNotNone(script_state)
    tx.close()



  def tearDown(self):
    """
    Tears down the test environment.
    """
    self.setup_test_paths()
    if self.kp_token.exists():
      os.remove(self.kp_token)
    if self.kp_path.exists():
      os.remove(self.kp_path)
    if self.prop_path.exists():
      os.remove(self.prop_path)
    if self.bp_path.exists():
      os.remove(self.bp_path)
    if self.kp_key.exists():
      os.remove(self.kp_key)


if __name__ == '__main__':
  unittest.main()
