import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.resources

from trapper_keeper.main import TrapperKeeper
from pykeepass.group import Group
from pykeepass.pykeepass import create_database

TEST_KEEPASS_DB_PATH: str = 'test_store.kdbx'
TEST_KEEPASS_DB_PATH_TMP: str = 'test_store_tmp.kdbx'
TEST_KEEPASS_DB_TOKEN: str = 'test_token'


class TestKeepassCase(unittest.TestCase):

    def setUp(self):
      self.db_path_ref = importlib.resources.files("tests.test_resources")
      self.db_pass: str = str(self.db_path_ref.joinpath(TEST_KEEPASS_DB_TOKEN))
      self.db_path: str = str(self.db_path_ref.joinpath(TEST_KEEPASS_DB_PATH))
      self.db_path_tmp: str = str(self.db_path_ref.joinpath(TEST_KEEPASS_DB_PATH_TMP))

      if not Path(self.db_path_tmp).exists():
        decoded_pass = Path(self.db_pass).read_text(encoding='utf-8')
        create_database(filename=self.db_path, password=decoded_pass, keyfile=None)

      shutil.copy(self.db_path, self.db_path_tmp)

    def tearDown(self):
      os.remove(self.db_path_tmp)

    def test_keepass_init(self):
      with TrapperKeeper(self.db_path, self.db_pass, None) as tkeeper:
        assert tkeeper is not None

    def test_keepass_group_add_delete(self):
      with TrapperKeeper(self.db_path_tmp, self.db_pass, None) as tkeeper_tmp:
        tkeeper_tmp.add_group(tkeeper_tmp.root_group, "test")
        tkeeper_tmp.save(self.db_path_tmp)
        result: Group = tkeeper_tmp.find_groups(name="test", first=True)
        assert result is not None
        assert isinstance(result, Group)
        assert result.name == "test"
        tkeeper_tmp.delete_group(result)
        result: Group = tkeeper_tmp.find_groups(name="test", first=True)
        assert result is None


    def test_kv_store(self):
      with TrapperKeeper(self.db_path_tmp, self.db_pass, None) as tkeeper_tmp:
        tkeeper_tmp.kv_store("test", "test")

      with TrapperKeeper(self.db_path_tmp, self.db_pass, None) as tkeeper_tmp:
        value: dict | str = tkeeper_tmp.kv_lookup("test")
        assert value == "test"


if __name__ == '__main__':
    unittest.main()
