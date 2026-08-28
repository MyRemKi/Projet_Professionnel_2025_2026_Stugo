# Tests unitaires pour Command / CommandHistory (app/commands/base_command.py)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.commands.base_command import Command, CommandHistory


class FakeCommand(Command):
    """Commande de test dont le comportement (succes/echec, undo) est controlable."""

    def __init__(self, name="fake", exec_result=True, undo_result=True, undoable=True):
        self.name = name
        self.exec_result = exec_result
        self.undo_result = undo_result
        self.undoable = undoable
        self.executed = False
        self.undone = False

    def execute(self) -> bool:
        self.executed = True
        return self.exec_result

    def undo(self) -> bool:
        self.undone = True
        return self.undo_result

    def can_undo(self) -> bool:
        return self.undoable

    @property
    def description(self) -> str:
        return self.name


class TestCommandDefaults(unittest.TestCase):

    def test_default_undo_returns_false(self):
        class MinimalCommand(Command):
            def execute(self) -> bool:
                return True
        cmd = MinimalCommand()
        self.assertFalse(cmd.undo())

    def test_default_can_undo_returns_false(self):
        class MinimalCommand(Command):
            def execute(self) -> bool:
                return True
        cmd = MinimalCommand()
        self.assertFalse(cmd.can_undo())

    def test_default_description_is_class_name(self):
        class MinimalCommand(Command):
            def execute(self) -> bool:
                return True
        self.assertEqual(MinimalCommand().description, "MinimalCommand")


class TestCommandHistoryExecute(unittest.TestCase):

    def test_successful_execute_is_recorded(self):
        history = CommandHistory()
        cmd = FakeCommand(exec_result=True)
        ok = history.execute(cmd)
        self.assertTrue(ok)
        self.assertIn(cmd, history.done)

    def test_failed_execute_is_not_recorded(self):
        history = CommandHistory()
        cmd = FakeCommand(exec_result=False)
        ok = history.execute(cmd)
        self.assertFalse(ok)
        self.assertNotIn(cmd, history.done)

    def test_max_size_trims_oldest(self):
        history = CommandHistory(max_size=2)
        cmds = [FakeCommand(name=f"c{i}") for i in range(3)]
        for cmd in cmds:
            history.execute(cmd)
        self.assertEqual(len(history.done), 2)
        self.assertNotIn(cmds[0], history.done)
        self.assertIn(cmds[1], history.done)
        self.assertIn(cmds[2], history.done)


class TestCommandHistoryUndo(unittest.TestCase):

    def test_undo_last_undoable_command(self):
        history = CommandHistory()
        cmd = FakeCommand(undoable=True, undo_result=True)
        history.execute(cmd)
        ok = history.undo_last()
        self.assertTrue(ok)
        self.assertTrue(cmd.undone)
        self.assertNotIn(cmd, history.done)

    def test_undo_last_skips_non_undoable_commands(self):
        history = CommandHistory()
        non_undoable = FakeCommand(name="a", undoable=False)
        undoable = FakeCommand(name="b", undoable=True)
        history.execute(non_undoable)
        history.execute(undoable)
        ok = history.undo_last()
        self.assertTrue(ok)
        self.assertTrue(undoable.undone)
        self.assertFalse(non_undoable.undone)
        self.assertIn(non_undoable, history.done)
        self.assertNotIn(undoable, history.done)

    def test_undo_last_on_empty_history_returns_false(self):
        history = CommandHistory()
        self.assertFalse(history.undo_last())

    def test_undo_last_keeps_command_when_undo_fails(self):
        history = CommandHistory()
        cmd = FakeCommand(undoable=True, undo_result=False)
        history.execute(cmd)
        ok = history.undo_last()
        self.assertFalse(ok)
        self.assertIn(cmd, history.done)

    def test_clear_empties_history(self):
        history = CommandHistory()
        history.execute(FakeCommand())
        history.clear()
        self.assertEqual(history.done, [])


if __name__ == "__main__":
    unittest.main()
