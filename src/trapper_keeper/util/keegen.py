"""Module to generate the keyfile and password from all printable characters.

Methods from [fauxfactory](https://github.com/omaciel/fauxfactory/tree/master)
"""
import random
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import unicodedata

from trapper_keeper.util.db_utils import KEEPASS_DB_KEY, KEEPASS_DB_TOKEN

TOKEN_SIZE: int = 40
KEY_SIZE: int = 190

UnicodePlane = namedtuple("UnicodePlane", ["min", "max"])
BMP = UnicodePlane(int("0x0000", 16), int("0xffff", 16))
SMP = UnicodePlane(int("0x10000", 16), int("0x1ffff", 16))

def _read_secret(secret: Path | None = None):
  return secret.read_text(encoding="utf-8")

def _create_secret(secret: Path | None = None):
  if secret is None:
    return None
  else:
    return _read_secret(secret)

def _write_secret(secret: tuple[Path, str]):
  with open(file=secret[0], encoding="utf-8", mode="x"):
    secret[0].write_text(secret[1])

@dataclass
class KeeAuth:
  """KeeAuth holds the two secrets (token & key) for keepass access.  If the file does not exist, a key will be generated"""
  _kp_token: tuple[Path, str | None] = (KEEPASS_DB_TOKEN, None)
  _kp_key: tuple[Path, str | None] = (KEEPASS_DB_KEY, None)

  @property
  def kp_token(self) -> tuple[Path, str]:
    return self._kp_token

  @kp_token.setter
  def kp_token(self, token: Path):
    if token.exists():
      self._kp_token = (token, _read_secret(token))
    else:
      self._kp_token = (token, gen_utf8(TOKEN_SIZE))

  @property
  def kp_key(self) -> tuple[Path, str]:
    return self._kp_key

  @kp_key.setter
  def kp_key(self, key: Path):
    if key.exists():
      self._kp_key = (key, _read_secret(key))
    else:
      self._kp_key = (key, gen_utf8(KEY_SIZE))

  def __iter__(self):
    yield self._kp_token
    yield self._kp_key

  def save(self):
    """Saves the KeeAuth secrets to their respective files, creating directories if necessary."""
    for secret in self:
        if secret is not None:
            secret[0].parent.mkdir(parents=True, exist_ok=True)
            _write_secret(secret)

  def items(self):
    return zip(self.__iter__(), self)

def gen_utf8(length=TOKEN_SIZE, smp=True, start=None, separator=""):
    """Return a random string made up of UTF-8 letters characters.

    Follows `RFC 3629`_.

    :param int length: Length for random data.
    :param str start: Random data start with.
    :param str separator: Separator character for start and random data.
    :param bool smp: Include Supplementary Multilingual Plane (SMP)
        characters
    :returns: A random string made up of ``UTF-8`` letters characters.
    :rtype: str

    .. _`RFC 3629`: http://www.rfc-editor.org/rfc/rfc3629.txt

    """
    unicode_letters = list(unicode_letters_generator(smp))
    output_string = "".join(random.choices(unicode_letters, k=length))

    if start:
        output_string = f"{start}{separator}{output_string}"[0:length]
    return output_string


def unicode_letters_generator(smp=True):
    """Generate unicode characters in the letters category.

    :param bool smp: Include Supplementary Multilingual Plane (SMP)
        characters
    :return: a generator which will generates all unicode letters available

    """
    for i in range(BMP.min, SMP.max if smp else BMP.max):
        char = chr(i)
        if unicodedata.category(char).startswith("L"):
            yield char
