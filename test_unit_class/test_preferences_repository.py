# Tests unitaires pour la classe PreferencesRepository (infrastructure/persistence/preferences_repository.py)

import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.persistence.preferences_repository import PreferencesRepository


class TestPreferencesRepository(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="stugo_prefs_test_")
        self.repo = PreferencesRepository()
        # On redirige vers un fichier temporaire pour ne jamais toucher les vraies preferences utilisateur.
        self.repo.prefs_file = os.path.join(self.tmp_dir, "prefs.json")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_load_returns_empty_dict_when_file_missing(self):
        self.assertEqual(self.repo.load(), {})

    def test_save_then_load_roundtrip(self):
        data = {"theme": "dark", "columns": ["zone", "pays"]}
        ok = self.repo.save(data)
        self.assertTrue(ok)
        self.assertEqual(self.repo.load(), data)

    def test_save_returns_true_on_success(self):
        self.assertTrue(self.repo.save({"a": 1}))

    def test_save_overwrites_previous_content(self):
        self.repo.save({"theme": "dark"})
        self.repo.save({"theme": "light"})
        self.assertEqual(self.repo.load(), {"theme": "light"})

    def test_load_returns_empty_dict_on_corrupted_file(self):
        os.makedirs(os.path.dirname(self.repo.prefs_file), exist_ok=True)
        with open(self.repo.prefs_file, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        self.assertEqual(self.repo.load(), {})

    def test_save_handles_non_serializable_data_gracefully(self):
        ok = self.repo.save({"bad": {1, 2, 3}})
        self.assertFalse(ok)

    def test_instance_returns_same_singleton(self):
        first = PreferencesRepository.instance()
        second = PreferencesRepository.instance()
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
