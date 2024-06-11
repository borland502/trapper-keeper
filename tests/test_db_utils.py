import tempfile
import unittest
from pathlib import Path

from boltdb import BoltDB
from boltdb.tx import Tx
from pykeepass.group import Group
from pykeepass.pykeepass import PyKeePass

from trapper_keeper.util.db_utils import DbUtils, SPECIAL_BINARIES
from trapper_keeper.util.keegen import KeeAuth


class TestKeepassCase(unittest.TestCase):

  def __init__(self, methodName: str = "runTest"):
    super().__init__(methodName)

  def setUp(self):
    """
    Sets up the test environment.
    """
    with tempfile.TemporaryDirectory(delete=False) as tmpdir:
      self.kp_key = Path(tmpdir, "key")
      self.kp_token = Path(tmpdir, "token")
      self.kp_db = Path(tmpdir, "kp.kdbx")
      self.prop_path = Path(tmpdir, "sqlite.sqlite")
      self.bolt_path = Path(tmpdir, "bolt.db")
      self.kee_auth: KeeAuth = KeeAuth()
      self.kee_auth.kp_key = self.kp_key
      self.kee_auth.kp_token = self.kp_token
      self.kee_auth.save()

  def test_create_tk_store(self):
    if not self.kp_db.exists():
      DbUtils.create_tk_store(kp_fp=self.kp_db, kp_token=self.kp_token, kp_key=self.kp_key, kv_fp=self.prop_path)
    self.assertTrue(self.kp_token.exists())
    self.assertTrue(self.kp_db.exists())
    with (PyKeePass(filename=self.kp_db, password=self.kp_token.read_text(encoding='utf-8'), keyfile=self.kp_key)) as kp_db:
      group: Group = kp_db.find_groups(name=SPECIAL_BINARIES, first=True)
      self.assertIsNotNone(group)
      self.assertEqual(SPECIAL_BINARIES, group.name)
      self.assertGreater(len(group.entries), 0)
      self.assertGreater(len(kp_db.attachments), 0)

  def test_chezmoi_bolt_db_rw(self):
    db: BoltDB = BoltDB(filename=self.bolt_path)
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

    bolt_db: BoltDB = DbUtils.load_boltdb_store(self.bolt_path)
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
    dir_parent: Path = self.kp_key.parent
    self.kp_key.unlink(missing_ok=True)
    self.kp_token.unlink(missing_ok=True)
    self.prop_path.unlink(missing_ok=True)
    self.bolt_path.unlink(missing_ok=True)
    self.kp_db.unlink(missing_ok=True)
    dir_parent.rmdir()


if __name__ == '__main__':
  unittest.main()
