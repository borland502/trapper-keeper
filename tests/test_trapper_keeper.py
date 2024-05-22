import unittest
import importlib.resources

from main import TrapperKeeper

TEST_KEEPASS_DB_PATH: str = 'test_store.kdbx'
TEST_KEEPASS_DB_TOKEN: str = 'test_token'


class TestKeepassCase(unittest.TestCase):

    def testKeePassInit(self):
        db_path_ref = importlib.resources.files("tests.resource")
        db_pass: str = str(db_path_ref.joinpath(TEST_KEEPASS_DB_TOKEN))
        db_path: str = str(db_path_ref.joinpath(TEST_KEEPASS_DB_PATH))

        with TrapperKeeper(db_path, db_pass, None) as tkeeper:
            assert tkeeper is not None


if __name__ == '__main__':
    unittest.main()
