import unittest

from firmware.common.controller_runtime import ControllerRuntime
from firmware.common.controller_web_bridge import ControllerWebBridge


class ControllerWebBridgeTests(unittest.TestCase):
    def test_sync_updates_web_state(self):
        runtime = ControllerRuntime()
        runtime.start()
        runtime.tick(1.0)

        bridge = ControllerWebBridge(runtime)
        bridge.sync()

        self.assertTrue(bridge.web_state.active)
        self.assertEqual(bridge.web_state.phase, "OCCUPY")
        self.assertLess(bridge.web_state.time_remaining_ms, 30000)


if __name__ == "__main__":
    unittest.main()
