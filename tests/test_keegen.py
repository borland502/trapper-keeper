import tempfile
import unittest
from pathlib import Path

from trapper_keeper.util.keegen import Keegen, KeeAuth


class TestGenAuth(unittest.TestCase):

  def __init__(self, methodName: str = "TestGenAuth"):
    super().__init__(methodName)

  def setUp(self):
    with tempfile.TemporaryDirectory(delete=False) as tmpdir:
      self.kp_key = Path(tmpdir, "key")
      self.kp_token = Path(tmpdir, "token")
      self.kee_auth: KeeAuth = Keegen.gen_auth(kp_key=self.kp_key, kp_token=self.kp_token)

  def test_gen_auth(self):
    self.assertIsNotNone(self.kee_auth)
    self.assertIsNotNone(self.kee_auth.kp_key)
    self.assertIsNotNone(self.kee_auth.kp_token)

    self.assertGreaterEqual(a=len(self.kee_auth.kp_token), b=Keegen.TOKEN_SIZE,
                            msg=f"Token is less than {Keegen.TOKEN_SIZE} bytes")
    self.assertGreaterEqual(a=len(self.kee_auth.kp_key), b=Keegen.KEY_SIZE,
                            msg=f"Key is less than {Keegen.KEY_SIZE} bytes")

  def test_file_equals(self):
    with open(self.kp_key, encoding="utf-8", mode="r", newline="\n") as f:
      self.assertEqual(first=f.read(), second=self.kee_auth.kp_key)

    with open(self.kp_token, encoding="utf-8", mode="r", newline="\n") as f:
      self.assertEqual(first=f.read(), second=self.kee_auth.kp_token)

  def tearDown(self):
    dir_folder:Path = self.kp_key.parent
    self.kp_key.unlink(missing_ok=True)
    self.kp_token.unlink(missing_ok=True)
    dir_folder.rmdir()
