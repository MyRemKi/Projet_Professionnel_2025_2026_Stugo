# Tests unitaires pour la classe SessionRepository (infrastructure/persistence/session_repository.py)

import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.persistence.session_repository import SessionRepository


class TestSessionRepository(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="stugo_session_test_")
        self.repo = SessionRepository()
        # On redirige vers un fichier temporaire pour ne jamais toucher la vraie session utilisateur.
        self.repo.session_file = os.path.join(self.tmp_dir, "session.json")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_read_returns_empty_dict_when_missing(self):
        missing_path = os.path.join(self.tmp_dir, "does_not_exist.json")
        self.assertEqual(self.repo.read(missing_path), {})

    def test_write_then_read_roundtrip(self):
        path = os.path.join(self.tmp_dir, "data.json")
        data = {"files": ["a.xlsx"], "filters": {"pays": "France"}}
        ok = self.repo.write(path, data)
        self.assertTrue(ok)
        self.assertEqual(self.repo.read(path), data)

    def test_write_creates_missing_parent_directories(self):
        path = os.path.join(self.tmp_dir, "nested", "sub", "data.json")
        ok = self.repo.write(path, {"a": 1})
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(path))

    def test_load_session_returns_empty_dict_when_no_session_saved(self):
        self.assertEqual(self.repo.load_session(), {})

    def test_save_session_then_load_session_roundtrip(self):
        data = {"loaded_files": ["a.csv", "b.csv"]}
        ok = self.repo.save_session(data)
        self.assertTrue(ok)
        self.assertEqual(self.repo.load_session(), data)

    def test_clear_session_removes_file(self):
        self.repo.save_session({"a": 1})
        self.assertTrue(os.path.exists(self.repo.session_file))
        ok = self.repo.clear_session()
        self.assertTrue(ok)
        self.assertFalse(os.path.exists(self.repo.session_file))

    def test_clear_session_when_no_file_exists_still_returns_true(self):
        self.assertFalse(os.path.exists(self.repo.session_file))
        self.assertTrue(self.repo.clear_session())

    def test_get_session_dir_returns_app_data_dir(self):
        from shared.paths import APP_DATA_DIR
        self.assertEqual(self.repo.get_session_dir(), APP_DATA_DIR)

    def test_instance_returns_same_singleton(self):
        first = SessionRepository.instance()
        second = SessionRepository.instance()
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
