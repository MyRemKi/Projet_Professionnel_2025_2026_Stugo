# Tests unitaires pour la classe AppState (presentation/state/app_state.py)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from presentation.state.app_state import AppState
from presentation.state.states import AppStateEnum


class TestAppState(unittest.TestCase):

    def setUp(self):
        # Instance dediee (pas le singleton) pour isoler chaque test.
        self.state = AppState()

    def test_initial_state_is_idle(self):
        self.assertEqual(self.state.current, AppStateEnum.IDLE)

    def test_transition_updates_current_state(self):
        self.state.transition(AppStateEnum.LOADING)
        self.assertEqual(self.state.current, AppStateEnum.LOADING)

    def test_transition_emits_state_changed_signal(self):
        received = []
        self.state.state_changed.connect(lambda s: received.append(s))
        self.state.transition(AppStateEnum.READY)
        self.assertEqual(received, [AppStateEnum.READY])

    def test_transition_to_same_state_does_not_emit(self):
        received = []
        self.state.state_changed.connect(lambda s: received.append(s))
        self.state.transition(AppStateEnum.IDLE)
        self.assertEqual(received, [])

    def test_is_ready_true_only_in_ready_state(self):
        self.assertFalse(self.state.is_ready())
        self.state.transition(AppStateEnum.READY)
        self.assertTrue(self.state.is_ready())

    def test_is_loading_true_only_in_loading_state(self):
        self.assertFalse(self.state.is_loading())
        self.state.transition(AppStateEnum.LOADING)
        self.assertTrue(self.state.is_loading())

    def test_instance_returns_same_singleton(self):
        first = AppState.instance()
        second = AppState.instance()
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
