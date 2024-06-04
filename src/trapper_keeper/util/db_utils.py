"""Utility module to create all the insecure stores to pack into KeePass"""

import contextlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from boltdb import BoltDB
from pykeepass.attachment import Attachment
from pykeepass.group import Entry, Group
from pykeepass.pykeepass import create_database, PyKeePass

from trapper_keeper import xdg_cache_home, xdg_data_home, xdg_config_home, xdg_state_home
from trapper_keeper.sqlite_kvstore import KeyValueStore

PROPERTIES_IDX: int = 0
KV_STORE: Path = Path(xdg_cache_home(), "trapper_keeper/kv_store.sqlite")
KEEPASS_DB_PATH: Path = Path.joinpath(xdg_data_home(), "trapper_keeper/secrets.kdbx")
KEEPASS_DB_KEY: Path = Path.joinpath(xdg_config_home(), "trapper_keeper/secrets.keyx")
KEEPASS_DB_TOKEN: Path = Path.joinpath(xdg_state_home(), "trapper_keeper/secrets_token")

SPECIAL_BINARIES: str = "2b405bc0-8583-491c-a4af-81628388f2c4"


class DbTypes(Enum):
  BOLT: str = "BoltDB"
  KP: str = "Keepass"
  SQLITE: str = "Sqlite"


class DbUtils:

  @classmethod
  def create_tk_store(cls, kp_fp: Path, kp_token: Path, kp_key: Path, kv_fp: Path | None = None) -> None:
    kp_db: PyKeePass = cls._create_kp_db(kp_fp=kp_fp, kp_token=kp_token, kp_key=kp_key)
    group: Group = cls._create_group(kp_db)
    cls._create_kv_store(kp_db, group, kv_fp)
    kp_db.save()
    # TODO: Validation on creation

  @classmethod
  def pack_tk_store(cls, kp_fp: Path, kp_token: Path, kp_key: Path, kv_fp: Path | None = None):
    with PyKeePass(filename=kp_fp, password=kp_token, keyfile=kp_key) as kp_db:
      binary_entry: Entry = kp_db.find_entries(title="Properties", first=True)
      properties_attachment: Attachment = binary_entry.attachments[PROPERTIES_IDX]
      binary_entry.delete_attachment(properties_attachment)
      binary_entry.add_attachment(id=PROPERTIES_IDX, filename=str(kv_fp))
      kp_db.save()

  @classmethod
  def unpack_tk_store(cls, kp_fp: Path, kp_token: Path, kp_key: Path | None = None):
    with PyKeePass(filename=kp_fp, password=kp_token, keyfile=kp_key) as kp_db:
      for attachment in kp_db.attachments:
        with open(file=attachment.filename, encoding='utf-8', mode="w+b") as attachment_update:
          attachment_update.write(attachment.binary)

  @staticmethod
  def _create_kp_db(kp_fp: Path, kp_token: Path, kp_key: Path | None = None) -> PyKeePass:
    """Create a new keepass vault in the KEEPASS_DB_PATH, with the KEEPASS_DB_KEY, and KEEPASS_DB_TOKEN."""
    if not kp_fp.is_file():
      # make the directory at least if the database does not exist
      kp_fp.parent.mkdir(mode=0o700, exist_ok=True, parents=True)
    else:
      # database exists
      raise FileExistsError(f"{kp_fp.name} exists in path {kp_fp.parent}")

    # Token and key must exist in the target destinations ahead of time
    if not kp_token.is_file():
      # make the directory at least if the database does not exist
      kp_token.parent.mkdir(mode=0o700, exist_ok=True, parents=True)
      raise FileNotFoundError(f"Token file not found in path {kp_token}")

    if kp_key is not None and not kp_key.is_file():
      # make the directory at least if the database does not exist
      kp_key.parent.mkdir(mode=0o700, exist_ok=True, parents=True)
      raise FileNotFoundError(f"Key file not found in path {kp_key}")

    return create_database(kp_fp, password=kp_token.read_text("utf-8").strip("\n"), keyfile=kp_key)

  @staticmethod
  def _create_group(kp_db: PyKeePass) -> Group:
    # Keepass database params are always expected, so these pertain to an embedded attachment
    group = kp_db.find_groups(name=SPECIAL_BINARIES, first=True)
    if group is None or len(group) == 0:
      group = kp_db.add_group(
        destination_group=kp_db.root_group,
        group_name=SPECIAL_BINARIES,
        notes="Special group dedicated to auxiliary data stores"
      )
      kp_db.save()
      return group
    else:
      raise AttributeError(f"Special binaries ({SPECIAL_BINARIES}) group already exists")

  @staticmethod
  def _create_kv_store(kp_db: PyKeePass, group: Group, kv_fp: Path = KV_STORE, prop_table_name: str = "Properties") -> KeyValueStore:
    properties_entry: Entry = kp_db.add_entry(destination_group=group, title=prop_table_name, username="", password="")

    """Create the sqlite database with a Key/Value store that is closed immediately after it exports the init sql"""
    kv_db = KeyValueStore(filename=kv_fp)

    # binary: bytes = bytes("".join(kv_db.iterdump()), "utf-8")
    properties_id: int = kp_db.add_binary(bytes(kv_db), protected=True)
    properties_entry.add_attachment(id=properties_id, filename=str(kv_fp))

    if not (len(kp_db.groups) > 0 and len(kp_db.entries) > 0 and len(kp_db.attachments) > 0 and len(kp_db.binaries) > 0):
      raise ValueError("Could not create special binary group in keepass db")

    kp_db.save()
    return kv_db

  @staticmethod
  def load_boltdb_store(bp_fp: Path) -> BoltDB:
    bolt_db = BoltDB(filename=bp_fp, readonly=True)
    return bolt_db
