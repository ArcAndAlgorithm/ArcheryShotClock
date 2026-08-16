import unittest

from firmware.common.timing_core import LightState, TimingConfig, TimingState


class TimingStateTests(unittest.TestCase):
    def test_start_sets_running_state(self):
        state = TimingState(config=TimingConfig(arrow_time_seconds=30.0, arrows_per_end=6))

        state.start()

        self.assertTrue(state.active)
        self.assertEqual(state.phase.value, "OCCUPY")
        self.assertEqual(state.light, LightState.GREEN)
        self.assertGreater(state.remaining_time, 0)

    def test_tick_counts_down_and_stops_at_zero(self):
        state = TimingState(config=TimingConfig(arrow_time_seconds=10.0, arrows_per_end=1))
        state.start()

        state.tick(9.0)

        self.assertTrue(state.active)
        self.assertAlmostEqual(state.remaining_time, 1.0)

        state.tick(1.0)

        self.assertFalse(state.active)
        self.assertEqual(state.light, LightState.RED)
        self.assertEqual(state.phase.value, "STOPPED")

    def test_pause_and_resume_recalculate_time(self):
        state = TimingState(config=TimingConfig(arrow_time_seconds=30.0, arrows_per_end=6))
        state.start()
        state.tick(60.0)
        state.register_arrow_shot()
        state.pause()

        state.resume()

        self.assertTrue(state.active)
        self.assertFalse(state.paused)
        self.assertEqual(state.phase.value, "OCCUPY")
        self.assertGreaterEqual(state.remaining_time, 150.0)

    def test_yellow_warning_appears_before_expiry(self):
        state = TimingState(config=TimingConfig(arrow_time_seconds=40.0, arrows_per_end=1, yellow_warning_seconds=30.0))
        state.start()

        state.tick(9.0)
        self.assertEqual(state.light, LightState.GREEN)

        state.tick(1.0)
        self.assertEqual(state.light, LightState.YELLOW)

        state.tick(15.0)
        self.assertEqual(state.light, LightState.YELLOW)


if __name__ == "__main__":
    unittest.main()
