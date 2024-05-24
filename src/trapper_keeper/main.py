# -*- coding: utf-8 -*-
from pathlib import Path

from pykeepass import PyKeePass
from xdg_base_dirs import xdg_data_home, xdg_config_home, xdg_state_home

KEEPASS_DB_PATH: str = str(Path.joinpath(xdg_data_home(), 'keepass/secrets.kdbx'))
KEEPASS_DB_KEY: str = str(Path.joinpath(xdg_config_home(), 'keepass/key.txt'))
KEEPASS_DB_TOKEN: str = str(Path.joinpath(xdg_state_home(), 'keepass/keepass_token'))


class TrapperKeeper(PyKeePass):
  """Trapper Keeper is a general project values/artifacts store using KeePassXC for secure artifacts
   and sqlite for insecure values/artifacts as well as keys for the secure elements."""

  def __enter__(self):
    super().__enter__()
    return self

  def __init__(self, db_path: str =KEEPASS_DB_PATH, password=KEEPASS_DB_TOKEN,
               keyfile: str | None = KEEPASS_DB_KEY):

    passwd: str = Path(password).read_text("utf-8")
    super().__init__(filename=db_path, password=passwd, keyfile=keyfile)

  def __exit__(self, exc_type, exc_val, exc_tb):
    super().__exit__(exc_type, exc_val, exc_tb)
    self.close()

  def close(self):
    pass
