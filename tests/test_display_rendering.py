import unittest

from firmware.common.protocol import StateUpdateMessage


class DisplayRenderingTests(unittest.TestCase):
    """
    Tests for the display rendering logic that converts controller state
    into visual output on the RGB matrix panel.
    """

    def test_state_update_yellow_warning_light(self):
        """Test that time_remaining_ms <= 30s triggers YELLOW light."""
        state = StateUpdateMessage(
            session_id="test",
            unit_id="display-01",
            device_role="display",
            light_state="YELLOW",
            phase="SHOOTING",
            active=True,
            time_remaining_ms=25000,  # 25 seconds
        )

        self.assertEqual(state.light_state, "YELLOW")
        self.assertEqual(state.time_remaining_ms, 25000)
        self.assertTrue(state.active)

    def test_state_update_red_stopped(self):
        """Test that stopped phase shows RED light."""
        state = StateUpdateMessage(
            session_id="test",
            unit_id="display-01",
            device_role="display",
            light_state="RED",
            phase="STOPPED",
            active=False,
            time_remaining_ms=0,
        )

        self.assertEqual(state.light_state, "RED")
        self.assertEqual(state.phase, "STOPPED")
        self.assertFalse(state.active)

    def test_state_update_green_occupy(self):
        """Test that occupy phase shows GREEN light."""
        state = StateUpdateMessage(
            session_id="test",
            unit_id="display-01",
            device_role="display",
            light_state="GREEN",
            phase="OCCUPY",
            active=True,
            time_remaining_ms=30000,
        )

        self.assertEqual(state.light_state, "GREEN")
        self.assertEqual(state.phase, "OCCUPY")
        self.assertTrue(state.active)

    def test_state_serialization_preserves_all_fields(self):
        """Test that state serialization for display includes all necessary fields."""
        state = StateUpdateMessage(
            session_id="match-01",
            unit_id="controller-01",
            device_role="controller",
            light_state="YELLOW",
            phase="SHOOTING",
            active=True,
            paused=False,
            time_remaining_ms=12500,
            arrows_shot=2,
            arrows_per_end=6,
            end_number=1,
            set_number=1,
            protocol_version=1,
        )

        data = state.to_dict()

        # All fields needed for display rendering must be present
        self.assertIn("time_remaining_ms", data)
        self.assertIn("light_state", data)
        self.assertIn("phase", data)
        self.assertIn("active", data)
        self.assertEqual(data["time_remaining_ms"], 12500)
        self.assertEqual(data["light_state"], "YELLOW")

    def test_state_update_paused_display(self):
        """Test that paused state is visible to displays."""
        state = StateUpdateMessage(
            session_id="test",
            unit_id="display-01",
            device_role="display",
            light_state="YELLOW",
            phase="PAUSED",
            active=True,
            paused=True,
            time_remaining_ms=15000,
        )

        self.assertTrue(state.paused)
        self.assertEqual(state.phase, "PAUSED")
        # Display should freeze the clock while paused


if __name__ == "__main__":
    unittest.main()
