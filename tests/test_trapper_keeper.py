import os
import shutil
import unittest
import importlib.resources

from trapper_keeper.main import TrapperKeeper
from pykeepass.group import Group

TEST_KEEPASS_DB_PATH: str = 'test_store.kdbx'
TEST_KEEPASS_DB_PATH_TMP: str = 'test_store_tmp.kdbx'
TEST_KEEPASS_DB_TOKEN: str = 'test_token'


class TestKeepassCase(unittest.TestCase):

    def setUp(self):
      db_path_ref = importlib.resources.files("tests.resource")
      db_pass: str = str(db_path_ref.joinpath(TEST_KEEPASS_DB_TOKEN))
      db_path: str = str(db_path_ref.joinpath(TEST_KEEPASS_DB_PATH))
      self.db_path_tmp: str = str(db_path_ref.joinpath(TEST_KEEPASS_DB_PATH_TMP))

      shutil.copy(db_path, self.db_path_tmp)
      self.tkeeper = TrapperKeeper(db_path, db_pass, None)
      self.tkeeper_tmp = TrapperKeeper(db_path, db_pass, None)

    def tearDown(self):
      self.tkeeper.close()
      self.tkeeper_tmp.close()
      os.remove(self.db_path_tmp)

    def test_keepass_init(self):
      assert self.tkeeper is not None

    def test_keepass_group_add_delete(self):
      self.tkeeper_tmp.add_group(self.tkeeper_tmp.root_group, "test")
      self.tkeeper_tmp.save(self.db_path_tmp)
      result: Group = self.tkeeper_tmp.find_groups(name="test", first=True)
      assert result is not None
      assert isinstance(result, Group)
      assert result.name == "test"
      self.tkeeper_tmp.delete_group(result)
      result: Group = self.tkeeper_tmp.find_groups(name="test", first=True)
      assert result is None


if __name__ == '__main__':
    unittest.main()
