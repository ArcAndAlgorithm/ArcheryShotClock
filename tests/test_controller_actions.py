import unittest

from firmware.common.controller_actions import ControllerActions
from firmware.common.controller_runtime import ControllerRuntime


class ControllerActionsTests(unittest.TestCase):
    def test_actions_change_runtime_state(self):
        runtime = ControllerRuntime()
        actions = ControllerActions(runtime)

        self.assertEqual(actions.start(), "STARTED")
        self.assertTrue(runtime.active)

        self.assertEqual(actions.pause(), "PAUSED")
        self.assertTrue(runtime.paused)

        self.assertEqual(actions.resume(), "RESUMED")
        self.assertFalse(runtime.paused)

        self.assertEqual(actions.emergency_stop(), "EMERGENCY_STOP")
        self.assertFalse(runtime.active)


if __name__ == "__main__":
    unittest.main()
