import unittest

from firmware.common.match_session import MatchSession, SessionConfig


class MatchSessionTests(unittest.TestCase):
    """Tests for integrated match session with timing and scoring."""

    def test_session_starts_and_runs_without_match_logic(self):
        config = SessionConfig(match_logic_enabled=False)
        session = MatchSession(config)

        session.start_match()
        self.assertTrue(session.timing.active)

        session.tick(5.0)
        self.assertGreater(session.timing.time_remaining_ms, 0)

    def test_session_starts_and_runs_with_match_logic(self):
        config = SessionConfig(
            match_logic_enabled=True,
            scoring_mode="CUMULATIVE",
            arrows_per_end=3,
            total_ends=2,
        )
        session = MatchSession(config)

        session.start_match()
        self.assertTrue(session.timing.active)
        self.assertIsNotNone(session.match_logic)
        self.assertTrue(session.match_logic.match_active)

    def test_add_arrow_score_with_match_logic(self):
        config = SessionConfig(
            match_logic_enabled=True,
            arrows_per_end=3,
        )
        session = MatchSession(config)
        session.start_match()

        result = session.add_arrow_score("9")
        self.assertTrue(result)
        self.assertEqual(len(session.match_logic.current_end_arrows), 1)

    def test_add_arrow_score_without_match_logic(self):
        config = SessionConfig(match_logic_enabled=False)
        session = MatchSession(config)

        result = session.add_arrow_score("9")
        self.assertFalse(result)  # No match logic to accept arrow

    def test_undo_arrow(self):
        config = SessionConfig(
            match_logic_enabled=True,
            arrows_per_end=3,
        )
        session = MatchSession(config)
        session.start_match()

        session.add_arrow_score("9")
        session.add_arrow_score("8")
        self.assertEqual(len(session.match_logic.current_end_arrows), 2)

        result = session.undo_arrow()
        self.assertTrue(result)
        self.assertEqual(len(session.match_logic.current_end_arrows), 1)

    def test_finalize_end_workflow(self):
        config = SessionConfig(
            match_logic_enabled=True,
            arrows_per_end=3,
            total_ends=2,
        )
        session = MatchSession(config)
        session.start_match()

        # Enter all arrows for end 1
        session.add_arrow_score("9")
        session.add_arrow_score("8")
        session.add_arrow_score("7")

        # Finalize end 1
        result = session.finalize_current_end()
        self.assertTrue(result)  # Match continues

        # Verify end was recorded
        set_score = session.match_logic.current_set()
        self.assertEqual(len(set_score.ends), 1)
        self.assertEqual(set_score.ends[0].total(), 24)

    def test_complete_match_workflow(self):
        config = SessionConfig(
            match_logic_enabled=True,
            arrows_per_end=3,
            total_ends=2,
        )
        session = MatchSession(config)
        session.start_match()

        # End 1
        session.add_arrow_score("9")
        session.add_arrow_score("8")
        session.add_arrow_score("7")
        result = session.finalize_current_end()
        self.assertTrue(result)

        # End 2
        session.add_arrow_score("X")
        session.add_arrow_score("9")
        session.add_arrow_score("8")
        result = session.finalize_current_end()
        self.assertFalse(result)  # Match ends

        self.assertFalse(session.match_logic.match_active)

    def test_pause_and_resume(self):
        config = SessionConfig(match_logic_enabled=False)
        session = MatchSession(config)
        session.start_match()

        self.assertTrue(session.timing.active)

        session.pause_match()
        self.assertTrue(session.timing.paused)

        session.resume_match()
        self.assertFalse(session.timing.paused)

    def test_get_full_state_without_match_logic(self):
        config = SessionConfig(match_logic_enabled=False)
        session = MatchSession(config)
        session.start_match()

        state = session.get_full_state()
        self.assertIn("config", state)
        self.assertIn("timing", state)
        self.assertNotIn("match", state)
        self.assertFalse(state["config"]["match_logic_enabled"])

    def test_get_full_state_with_match_logic(self):
        config = SessionConfig(
            match_logic_enabled=True,
            scoring_mode="CUMULATIVE",
            arrows_per_end=3,
        )
        session = MatchSession(config)
        session.start_match()
        session.add_arrow_score("9")

        state = session.get_full_state()
        self.assertIn("config", state)
        self.assertIn("timing", state)
        self.assertIn("match", state)
        self.assertTrue(state["config"]["match_logic_enabled"])
        self.assertEqual(state["match"]["current_arrows_in_end"], 1)

    def test_set_play_mode_workflow(self):
        config = SessionConfig(
            match_logic_enabled=True,
            scoring_mode="SET_PLAY",
            arrows_per_end=3,
            total_ends=3,
        )
        session = MatchSession(config)
        session.start_match()

        self.assertEqual(len(session.match_logic.sets), 1)

        # Advance to set 2
        result = session.advance_to_next_set()
        self.assertTrue(result)
        self.assertEqual(len(session.match_logic.sets), 2)


if __name__ == "__main__":
    unittest.main()
