"""Module to generate the keyfile and password from all printable characters"""
import string
import random
import time
from pathlib import Path

from trapper_keeper.util.db_utils import KeeAuth


class Keegen():

  TOKEN_SIZE: int = 40
  KEY_SIZE: int = 190

  @classmethod
  def gen_auth(cls, kp_token: Path | None = None, kp_key: Path | None = None):
    key_auth: KeeAuth = KeeAuth()
    if kp_token.is_file():
      key_auth.kp_token = kp_token.read_text(encoding="utf-8").strip("\n").strip("\r")
      key_auth.kp_key = kp_key.read_text(encoding="utf-8").strip("\n").strip("\r")
    else:
      key_auth.kp_token = ''.join(random.choices(string.printable, k=cls.TOKEN_SIZE)).strip("\n").strip("\r")
      with open(kp_token, "x", encoding="utf-8", newline="\n") as f:
        f.write(key_auth.kp_token)
      key_auth.kp_key = ''.join(random.choices(string.printable, k=cls.KEY_SIZE)).strip("\n").strip("\r")
      with open(kp_key, "x", encoding="utf-8", newline="\n") as f:
        f.write(key_auth.kp_key)

    return key_auth


if __name__ == '__main__':
    print(Keegen.gen_auth(kp_token=Path(f"/tmp/token_{time.time()}"), kp_key=Path(f"/tmp/token_{time.time()}")))
