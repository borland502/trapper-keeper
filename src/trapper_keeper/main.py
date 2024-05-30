# -*- coding: utf-8 -*-
import os
import pathlib
from pathlib import Path
from typing import Any
import ntpath

from pykeepass import PyKeePass
from pykeepass.group import Group
from pykeepass.entry import Entry
from pykeepass.attachment import Attachment
from sqlite_utils import Database
from xdg_base_dirs import xdg_data_home, xdg_config_home, xdg_state_home, xdg_cache_home

SPECIAL_BINARIES: str = "2b405bc0-8583-491c-a4af-81628388f2c4"
PROPERTIES_TABLE: str = "properties"
PROPERTIES_IDX: int = 0
KV_STORE: Path = Path.joinpath(xdg_cache_home(), 'keepass/kv_store.sqlite')
KEEPASS_DB_PATH: str = str(Path.joinpath(xdg_data_home(), 'keepass/secrets.kdbx'))
KEEPASS_DB_KEY: str = str(Path.joinpath(xdg_config_home(), 'keepass/key.txt'))
KEEPASS_DB_TOKEN: str = str(Path.joinpath(xdg_state_home(), 'keepass/keepass_token'))

class TrapperKeeper(PyKeePass):
  """Trapper Keeper is a general project values/artifacts store using KeePassXC for secure artifacts
   and sqlite for insecure values/artifacts as well as keys for the secure elements."""

  tk_db: Database

  def __enter__(self):
    super().__enter__()

    if KV_STORE.exists():
      os.remove(KV_STORE)

    self.tk_db = Database(KV_STORE)

    if len(self.attachments) == 0:
      binary_group: Group = self.add_group(destination_group=self.root_group, group_name=SPECIAL_BINARIES)
      properties_entry: Entry = self.add_entry(destination_group=binary_group, title=PROPERTIES_TABLE, username="automation",
                                           password="automation")
      binary: bytes = bytes("".join(self.tk_db.iterdump()), 'utf-8')
      self.properties_id: int = self.add_binary(binary, protected=False)
      properties_entry.add_attachment(id=self.properties_id, filename=str(KV_STORE))
      self.save()
    else:
      # find existing attachment/binary id
      properties_attachment: Attachment = self.find_attachments(filename=str(KV_STORE), first=True)
      KV_STORE.parent.mkdir(exist_ok=True)

      # unpack stored database
      self.tk_db.executescript(str(properties_attachment.binary, 'utf-8'))

    return self

  def __init__(self, db_path: str = KEEPASS_DB_PATH, password=KEEPASS_DB_TOKEN,
               keyfile: str | None = KEEPASS_DB_KEY):

    passwd: str = Path(password).read_text("utf-8")
    super().__init__(filename=db_path, password=passwd, keyfile=keyfile)

  def kv_lookup(self, key: str) -> dict:
    """Retrieve a value by key"""
    return self.tk_db.table(PROPERTIES_TABLE).lookup(lookup_values={"key": key}, pk="key")

  def kv_store(self, key: str, value: str):
    """Key/value generalized "properties" bucket: insecure."""
    self.tk_db.table(
      PROPERTIES_TABLE,
      pk="key",
      not_null={"key"},
      column_order=("key", "value")
    ).upsert(record={
      "key": key,
      "value": value
    },alter=True)

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.tk_db.close()
    binary_entry: Entry = self.find_entries(title=PROPERTIES_TABLE, first=True)
    properties_attachment: Attachment = binary_entry.attachments[PROPERTIES_IDX]
    binary_entry.delete_attachment(properties_attachment)
    binary_entry.add_attachment(id=PROPERTIES_IDX, filename=str(KV_STORE))
    self.save()
    os.remove(KV_STORE)
    super().__exit__(exc_type, exc_val, exc_tb)
