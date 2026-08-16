import unittest

from firmware.common.match_logic import ArrowScore, EndScore, SetScore, MatchLogic


class ArrowScoreTests(unittest.TestCase):
    """Tests for individual arrow scoring."""

    def test_arrow_score_numeric_value_0_to_9(self):
        for i in range(10):
            score = ArrowScore(arrow_index=0, score_value=str(i))
            self.assertEqual(score.numeric_value(), i)

    def test_arrow_score_x_is_10(self):
        score = ArrowScore(arrow_index=0, score_value="X")
        self.assertEqual(score.numeric_value(), 10)

    def test_arrow_score_10_is_10(self):
        score = ArrowScore(arrow_index=0, score_value="10")
        self.assertEqual(score.numeric_value(), 10)

    def test_arrow_score_m_is_0(self):
        score = ArrowScore(arrow_index=0, score_value="M")
        self.assertEqual(score.numeric_value(), 0)


class EndScoreTests(unittest.TestCase):
    """Tests for end scoring."""

    def test_end_score_total(self):
        end = EndScore(end_number=1)
        end.add_arrow("9")
        end.add_arrow("8")
        end.add_arrow("7")
        end.add_arrow("6")
        end.add_arrow("5")
        end.add_arrow("4")
        self.assertEqual(end.total(), 39)

    def test_end_score_with_X(self):
        end = EndScore(end_number=1)
        end.add_arrow("X")
        end.add_arrow("9")
        end.add_arrow("8")
        end.add_arrow("7")
        end.add_arrow("6")
        end.add_arrow("5")
        self.assertEqual(end.total(), 45)

    def test_end_score_with_misses(self):
        end = EndScore(end_number=1)
        end.add_arrow("M")
        end.add_arrow("5")
        end.add_arrow("M")
        end.add_arrow("3")
        end.add_arrow("M")
        end.add_arrow("2")
        self.assertEqual(end.total(), 10)

    def test_end_score_is_complete_3_arrows(self):
        end = EndScore(end_number=1)
        end.add_arrow("5")
        self.assertFalse(end.is_complete(3))
        end.add_arrow("6")
        self.assertFalse(end.is_complete(3))
        end.add_arrow("7")
        self.assertTrue(end.is_complete(3))

    def test_end_score_is_complete_6_arrows(self):
        end = EndScore(end_number=1)
        for i in range(6):
            end.add_arrow("5")
        self.assertTrue(end.is_complete(6))


class SetScoreTests(unittest.TestCase):
    """Tests for set scoring."""

    def test_set_score_current_end_number(self):
        set_score = SetScore(set_number=1)
        self.assertEqual(set_score.current_end_number(), 1)
        set_score.add_end_score(EndScore(end_number=1))
        self.assertEqual(set_score.current_end_number(), 2)

    def test_set_score_total_for_athlete_a(self):
        set_score = SetScore(set_number=1)
        end1 = EndScore(end_number=1)
        end1.add_arrow("9")
        end1.add_arrow("8")
        end1.add_arrow("7")
        set_score.add_end_score(end1)

        end2 = EndScore(end_number=2)
        end2.add_arrow("X")
        end2.add_arrow("9")
        end2.add_arrow("8")
        set_score.add_end_score(end2)

        self.assertEqual(set_score.total_for_athlete_a(), 24 + 27)

    def test_set_score_to_dict(self):
        set_score = SetScore(set_number=1)
        end = EndScore(end_number=1)
        end.add_arrow("5")
        end.add_arrow("6")
        set_score.add_end_score(end)

        data = set_score.to_dict()
        self.assertEqual(data["set_number"], 1)
        self.assertEqual(data["ends_completed"], 1)
        self.assertEqual(data["athlete_a_total"], 11)


class MatchLogicTests(unittest.TestCase):
    """Tests for match logic and match flow."""

    def setUp(self):
        self.match = MatchLogic(
            event_type="INDIVIDUAL",
            round_type="QUALIFICATION",
            scoring_mode="CUMULATIVE",
            arrows_per_end=3,
            total_ends=2,
        )

    def test_match_start(self):
        self.match.start_match()
        self.assertTrue(self.match.match_active)
        self.assertEqual(len(self.match.sets), 1)

    def test_add_arrow_score(self):
        self.match.start_match()
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        self.assertEqual(len(self.match.current_end_arrows), 2)

    def test_cannot_add_more_arrows_than_per_end(self):
        self.match.start_match()
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        self.match.add_arrow_score("7")
        self.assertEqual(len(self.match.current_end_arrows), 3)
        # Trying to add a 4th arrow should not change the count
        self.match.add_arrow_score("6")
        self.assertEqual(len(self.match.current_end_arrows), 3)

    def test_undo_last_arrow(self):
        self.match.start_match()
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        self.assertEqual(len(self.match.current_end_arrows), 2)

        self.match.undo_last_arrow()
        self.assertEqual(len(self.match.current_end_arrows), 1)

        self.match.undo_last_arrow()
        self.assertEqual(len(self.match.current_end_arrows), 0)

    def test_finalize_end_with_correct_arrows(self):
        self.match.start_match()
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        self.match.add_arrow_score("7")

        result = self.match.finalize_end()
        self.assertTrue(result)  # Match continues

        set_score = self.match.current_set()
        self.assertEqual(len(set_score.ends), 1)
        self.assertEqual(set_score.ends[0].total(), 24)

    def test_cannot_finalize_incomplete_end(self):
        self.match.start_match()
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        # Missing 3rd arrow

        result = self.match.finalize_end()
        self.assertFalse(result)  # End not ready

    def test_finalize_last_end_ends_match(self):
        self.match.start_match()

        # End 1
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        self.match.add_arrow_score("7")
        result = self.match.finalize_end()
        self.assertTrue(result)  # Match continues

        # End 2 (last)
        self.match.add_arrow_score("X")
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")
        result = self.match.finalize_end()
        self.assertFalse(result)  # Match ends

        self.assertFalse(self.match.match_active)

    def test_get_match_state(self):
        self.match.start_match()
        self.match.add_arrow_score("9")
        self.match.add_arrow_score("8")

        state = self.match.get_match_state()
        self.assertEqual(state["event_type"], "INDIVIDUAL")
        self.assertEqual(state["scoring_mode"], "CUMULATIVE")
        self.assertEqual(state["current_arrows_in_end"], 2)
        self.assertTrue(state["match_active"])

    def test_set_play_mode(self):
        match = MatchLogic(
            event_type="INDIVIDUAL",
            round_type="FINALS",
            scoring_mode="SET_PLAY",
            arrows_per_end=3,
            total_ends=3,
        )
        match.start_match()
        self.assertEqual(len(match.sets), 1)

        # Advance to a new set
        result = match.advance_set()
        self.assertTrue(result)
        self.assertEqual(len(match.sets), 2)


if __name__ == "__main__":
    unittest.main()
