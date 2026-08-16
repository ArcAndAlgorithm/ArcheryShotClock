from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ArrowScore:
    """A single arrow's score (0-10, 'X' for 10, 'M' for miss)."""

    arrow_index: int = 0  # 0-indexed within the end
    score_value: str = "M"  # "0"-"9", "10", "X", "M"

    def numeric_value(self) -> int:
        """Convert score to numeric value for calculation."""
        if self.score_value == "X" or self.score_value == "10":
            return 10
        if self.score_value == "M":
            return 0
        try:
            return int(self.score_value)
        except ValueError:
            return 0


@dataclass
class EndScore:
    """Scores for all arrows in a single end."""

    end_number: int = 1
    arrows: List[ArrowScore] = field(default_factory=list)

    def total(self) -> int:
        """Sum of all arrow scores for this end."""
        return sum(arrow.numeric_value() for arrow in self.arrows)

    def is_complete(self, arrows_per_end: int) -> bool:
        """Check if all required arrows have been scored."""
        return len(self.arrows) >= arrows_per_end

    def add_arrow(self, score_value: str) -> None:
        """Record a single arrow score."""
        arrow_index = len(self.arrows)
        self.arrows.append(ArrowScore(arrow_index=arrow_index, score_value=score_value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "end_number": self.end_number,
            "arrow_count": len(self.arrows),
            "total": self.total(),
            "arrows": [{"index": a.arrow_index, "value": a.score_value} for a in self.arrows],
        }


@dataclass
class SetScore:
    """Scores and ends for a single set."""

    set_number: int = 1
    ends: List[EndScore] = field(default_factory=list)
    athlete_a_set_points: int = 0
    athlete_b_set_points: int = 0

    def current_end_number(self) -> int:
        """The end number currently being shot (1-indexed)."""
        return len(self.ends) + 1

    def add_end_score(self, end_score: EndScore) -> None:
        """Record scores for a completed end."""
        self.ends.append(end_score)

    def total_for_athlete_a(self) -> int:
        """Sum of all arrow scores for athlete A in this set."""
        return sum(end.total() for end in self.ends)

    def total_for_athlete_b(self) -> int:
        """Sum of all arrow scores for athlete B in this set (if applicable)."""
        # In alternating modes, B shoots in odd-numbered ends.
        # For simplicity, this is a placeholder for future alternating logic.
        return 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_number": self.set_number,
            "ends_completed": len(self.ends),
            "athlete_a_total": self.total_for_athlete_a(),
            "athlete_a_set_points": self.athlete_a_set_points,
            "athlete_b_set_points": self.athlete_b_set_points,
            "ends": [end.to_dict() for end in self.ends],
        }


class MatchLogic:
    """
    Optional scoring and match-state layer on top of the timing engine.
    Tracks ends, sets, arrows, and scores per World Archery rules.

    Supports two modes:
    - Set-play: First to win N sets (common in finals)
    - Cumulative: All ends contribute to a running total (common in qualification)
    """

    def __init__(
        self,
        event_type: str = "INDIVIDUAL",  # INDIVIDUAL, TEAM, MIXED_TEAM
        round_type: str = "QUALIFICATION",  # QUALIFICATION, MATCH_PLAY, FINALS
        scoring_mode: str = "CUMULATIVE",  # CUMULATIVE or SET_PLAY
        arrows_per_end: int = 6,
        total_ends: int = 12,
    ) -> None:
        self.event_type = event_type
        self.round_type = round_type
        self.scoring_mode = scoring_mode
        self.arrows_per_end = arrows_per_end
        self.total_ends = total_ends

        self.sets: List[SetScore] = [SetScore(set_number=1)]
        self.current_end_arrows: List[ArrowScore] = []
        self.match_active = False

    def start_match(self) -> None:
        """Begin a new match."""
        self.match_active = True
        self.sets = [SetScore(set_number=1)]
        self.current_end_arrows = []

    def current_set(self) -> SetScore:
        """Get the active set."""
        if not self.sets:
            self.sets.append(SetScore(set_number=1))
        return self.sets[-1]

    def add_arrow_score(self, score_value: str) -> None:
        """
        Record an arrow score (e.g., "0"-"9", "10", "X", "M").
        Called by score-entry UI before the end is finalized.
        """
        arrow_index = len(self.current_end_arrows)
        if arrow_index < self.arrows_per_end:
            self.current_end_arrows.append(
                ArrowScore(arrow_index=arrow_index, score_value=score_value)
            )

    def undo_last_arrow(self) -> bool:
        """Remove the last arrow score (for correction before end finalization)."""
        if self.current_end_arrows:
            self.current_end_arrows.pop()
            return True
        return False

    def finalize_end(self) -> bool:
        """
        Mark the current end as complete and move to the next end.
        Returns True if the match continues, False if the match is complete.
        """
        if len(self.current_end_arrows) != self.arrows_per_end:
            return False  # End not ready (missing arrows)

        set_score = self.current_set()
        end_number = set_score.current_end_number()
        end_score = EndScore(end_number=end_number, arrows=self.current_end_arrows)
        set_score.add_end_score(end_score)
        self.current_end_arrows = []

        # Check if match is complete
        if end_number >= self.total_ends:
            self.match_active = False
            return False

        return True

    def advance_set(self) -> bool:
        """
        Move to the next set (in set-play mode).
        Returns True on success, False if already at the final set.
        """
        if self.scoring_mode != "SET_PLAY":
            return False

        new_set = SetScore(set_number=len(self.sets) + 1)
        self.sets.append(new_set)
        self.current_end_arrows = []
        return True

    def get_match_state(self) -> Dict[str, Any]:
        """Get the full match state for display/persistence."""
        return {
            "event_type": self.event_type,
            "round_type": self.round_type,
            "scoring_mode": self.scoring_mode,
            "arrows_per_end": self.arrows_per_end,
            "total_ends": self.total_ends,
            "match_active": self.match_active,
            "sets": [set_score.to_dict() for set_score in self.sets],
            "current_arrows_in_end": len(self.current_end_arrows),
        }
