import unittest

from firmware.common.broadcast import BroadcastMessage, BroadcastTransport


class BroadcastTransportTests(unittest.TestCase):
    def test_state_message_reaches_all_listeners(self):
        channel = BroadcastTransport()
        received = []

        channel.subscribe(received.append)
        channel.publish_state({"session_id": "match-01", "phase": "SHOOTING", "light_state": "GREEN"})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["message_type"], "STATE_UPDATE")
        self.assertEqual(received[0]["session_id"], "match-01")

    def test_signal_message_reaches_all_listeners(self):
        channel = BroadcastTransport()
        received = []

        channel.subscribe(received.append)
        channel.publish_signal({"session_id": "match-01", "event_name": "SIGNAL_STOP", "count": 2})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["message_type"], "SIGNAL_EVENT")
        self.assertEqual(received[0]["event_name"], "SIGNAL_STOP")

    def test_message_has_protocol_version(self):
        message = BroadcastMessage("STATE_UPDATE", {"session_id": "match-01"})

        self.assertEqual(message.payload["session_id"], "match-01")
        self.assertEqual(message.payload["protocol_version"], 1)
        self.assertEqual(message.message_type, "STATE_UPDATE")


if __name__ == "__main__":
    unittest.main()
