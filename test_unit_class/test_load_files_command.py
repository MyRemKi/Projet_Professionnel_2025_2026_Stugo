# Tests unitaires pour LoadFilesCommand (app/commands/load_files_command.py)

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.commands.load_files_command import LoadFilesCommand


class TestLoadFilesCommand(unittest.TestCase):

    def setUp(self):
        self.data_service = MagicMock(name="data_service")
        self.paths = ["a.xlsx", "b.csv"]

    def test_execute_returns_true_when_files_loaded(self):
        self.data_service.load_files.return_value = {"uid1", "uid2"}
        cmd = LoadFilesCommand(self.paths, self.data_service)
        ok = cmd.execute()
        self.assertTrue(ok)
        self.data_service.load_files.assert_called_once_with(self.paths)
        self.assertEqual(cmd.loaded, {"uid1", "uid2"})

    def test_execute_returns_false_when_nothing_loaded(self):
        self.data_service.load_files.return_value = set()
        cmd = LoadFilesCommand(self.paths, self.data_service)
        ok = cmd.execute()
        self.assertFalse(ok)

    def test_execute_returns_false_on_exception(self):
        self.data_service.load_files.side_effect = RuntimeError("boom")
        cmd = LoadFilesCommand(self.paths, self.data_service)
        ok = cmd.execute()
        self.assertFalse(ok)

    def test_can_undo_reflects_loaded_state(self):
        cmd = LoadFilesCommand(self.paths, self.data_service)
        self.assertFalse(cmd.can_undo())
        cmd.loaded = {"uid1"}
        self.assertTrue(cmd.can_undo())

    def test_undo_removes_every_loaded_file(self):
        self.data_service.load_files.return_value = {"uid1", "uid2"}
        cmd = LoadFilesCommand(self.paths, self.data_service)
        cmd.execute()
        ok = cmd.undo()
        self.assertTrue(ok)
        called_uids = {call.args[0] for call in self.data_service.remove_file.call_args_list}
        self.assertEqual(called_uids, {"uid1", "uid2"})

    def test_undo_returns_false_on_exception(self):
        self.data_service.load_files.return_value = {"uid1"}
        cmd = LoadFilesCommand(self.paths, self.data_service)
        cmd.execute()
        self.data_service.remove_file.side_effect = RuntimeError("boom")
        self.assertFalse(cmd.undo())

    def test_description_mentions_file_count(self):
        cmd = LoadFilesCommand(self.paths, self.data_service)
        self.assertEqual(cmd.description, "Chargement 2 fichier(s)")


if __name__ == "__main__":
    unittest.main()
