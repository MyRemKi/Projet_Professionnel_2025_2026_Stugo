# Tests unitaires pour la classe EventBus (app/events/event_bus.py)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.events.event_bus import EventBus


class TestEventBusPubSub(unittest.TestCase):

    def setUp(self):
        # Instance dediee (pas le singleton) pour isoler chaque test.
        self.bus = EventBus()

    def test_subscriber_receives_published_payload(self):
        received = []
        self.bus.subscribe("files_loaded", lambda payload: received.append(payload))
        self.bus.publish("files_loaded", {"count": 3})
        self.assertEqual(received, [{"count": 3}])

    def test_publish_without_subscriber_does_not_raise(self):
        try:
            self.bus.publish("nobody_listens", 42)
        except Exception as e:
            self.fail(f"publish() a leve une exception: {e}")

    def test_multiple_subscribers_all_called(self):
        calls = []
        self.bus.subscribe("evt", lambda p: calls.append(("a", p)))
        self.bus.subscribe("evt", lambda p: calls.append(("b", p)))
        self.bus.publish("evt", "payload")
        self.assertEqual(sorted(calls), [("a", "payload"), ("b", "payload")])

    def test_unsubscribe_stops_future_notifications(self):
        received = []
        handler = lambda payload: received.append(payload)
        self.bus.subscribe("evt", handler)
        self.bus.unsubscribe("evt", handler)
        self.bus.publish("evt", "x")
        self.assertEqual(received, [])

    def test_unsubscribe_unknown_handler_does_not_raise(self):
        try:
            self.bus.unsubscribe("evt", lambda payload: None)
        except Exception as e:
            self.fail(f"unsubscribe() a leve une exception: {e}")

    def test_handler_exception_does_not_stop_other_handlers(self):
        received = []

        def bad_handler(payload):
            raise RuntimeError("boom")

        def good_handler(payload):
            received.append(payload)

        self.bus.subscribe("evt", bad_handler)
        self.bus.subscribe("evt", good_handler)
        self.bus.publish("evt", "x")
        self.assertEqual(received, ["x"])

    def test_instance_returns_same_singleton(self):
        first = EventBus.instance()
        second = EventBus.instance()
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
