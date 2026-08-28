# Tests unitaires pour ApplyFilterCommand (app/commands/apply_filter_command.py)

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.commands.apply_filter_command import ApplyFilterCommand


class TestApplyFilterCommand(unittest.TestCase):

    def setUp(self):
        self.sidebar = MagicMock(name="filter_sidebar")
        self.data_service = MagicMock(name="data_service")

    def test_execute_calls_apply_filters_with_sidebar(self):
        cmd = ApplyFilterCommand(self.sidebar, self.data_service)
        ok = cmd.execute()
        self.assertTrue(ok)
        self.data_service.apply_filters.assert_called_once_with(self.sidebar)

    def test_execute_returns_false_on_exception(self):
        self.data_service.apply_filters.side_effect = RuntimeError("boom")
        cmd = ApplyFilterCommand(self.sidebar, self.data_service)
        ok = cmd.execute()
        self.assertFalse(ok)

    def test_description(self):
        cmd = ApplyFilterCommand(self.sidebar, self.data_service)
        self.assertEqual(cmd.description, "Application des filtres")

    def test_is_not_undoable_by_default(self):
        cmd = ApplyFilterCommand(self.sidebar, self.data_service)
        self.assertFalse(cmd.can_undo())
        self.assertFalse(cmd.undo())


if __name__ == "__main__":
    unittest.main()
