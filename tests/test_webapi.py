import json
import threading
import time
import unittest
from urllib.request import urlopen

from firmware.common.webapi import WebControllerState, run_web_server


class WebApiTests(unittest.TestCase):
    def test_state_endpoint_returns_json(self):
        state = WebControllerState(
            active=True,
            paused=False,
            phase="OCCUPY",
            light_state="GREEN",
            time_remaining_ms=15000,
            arrows_shot=2,
            arrows_per_end=6,
            session_id="match-01",
        )
        server = run_web_server(state, host="127.0.0.1", port=8081)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            response = urlopen("http://127.0.0.1:8081/api/state")
            payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(payload["session_id"], "match-01")
            self.assertTrue(payload["active"])
            self.assertEqual(payload["light_state"], "GREEN")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
