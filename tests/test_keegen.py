import tempfile
import unittest
from pathlib import Path

from trapper_keeper.util import keegen
from trapper_keeper.util.keegen import KeeAuth


class TestGenAuth(unittest.TestCase):

  def __init__(self, methodName: str = "TestGenAuth"):
    super().__init__(methodName)

  def setUp(self):
    with tempfile.TemporaryDirectory(delete=False) as tmpdir:
      self.kp_key = Path(tmpdir, "key")
      self.kp_token = Path(tmpdir, "token")
      self.kee_auth: KeeAuth = KeeAuth()
      try:
        self.kee_auth.save()
        self.fail("FileExistError not raised")
      except FileExistsError:
        pass

      self.kee_auth_existing: KeeAuth = KeeAuth()
      self.kee_auth_existing.kp_key = self.kp_key
      self.kee_auth_existing.kp_token = self.kp_token
      self.kee_auth_existing.save()

  def test_gen_auth(self):
    self.assertIsNotNone(self.kee_auth_existing)
    self.assertGreaterEqual(a=len(self.kee_auth_existing.kp_key[1]), b=keegen.KEY_SIZE,
                            msg=f"Key is less than {keegen.KEY_SIZE} bytes")

  def test_file_equals(self):
    self.assertEqual(first=self.kp_token.read_text(encoding="utf-8"), second=self.kee_auth_existing.kp_token[1])
    self.assertEqual(first=self.kp_key.read_text(encoding="utf-8"), second=self.kee_auth_existing.kp_key[1])


  def tearDown(self):
    dir_folder:Path = self.kp_key.parent
    self.kp_key.unlink(missing_ok=True)
    self.kp_token.unlink(missing_ok=True)
    dir_folder.rmdir()
