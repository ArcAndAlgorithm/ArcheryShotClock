from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional

from firmware.common.controller_runtime import ControllerRuntime
from firmware.common.match_logic import MatchLogic


@dataclass
class SessionConfig:
    """Configuration for a match session."""

    event_type: str = "INDIVIDUAL"  # INDIVIDUAL, TEAM, MIXED_TEAM
    round_type: str = "QUALIFICATION"  # QUALIFICATION, MATCH_PLAY, FINALS
    match_logic_enabled: bool = False
    scoring_mode: str = "CUMULATIVE"  # CUMULATIVE or SET_PLAY
    arrows_per_end: int = 6
    total_ends: int = 12
    per_arrow_time_seconds: float = 30.0


class MatchSession:
    """
    High-level match session controller that coordinates timing and match logic.
    This sits above the individual ControllerRuntime and MatchLogic modules,
    unifying them into a single coherent match.
    """

    def __init__(self, config: SessionConfig) -> None:
        self.config = config
        self.timing = ControllerRuntime(
            session_id="session-01",
            unit_id="controller-01",
            arrows_per_end=config.arrows_per_end,
        )
        self.match_logic: Optional[MatchLogic] = None
        if config.match_logic_enabled:
            self.match_logic = MatchLogic(
                event_type=config.event_type,
                round_type=config.round_type,
                scoring_mode=config.scoring_mode,
                arrows_per_end=config.arrows_per_end,
                total_ends=config.total_ends,
            )

    def start_match(self) -> None:
        """Begin a new match."""
        self.timing.start()
        if self.match_logic:
            self.match_logic.start_match()

    def tick(self, delta_seconds: float) -> None:
        """Advance the clock by delta_seconds."""
        self.timing.tick(delta_seconds)

    def stop_match(self) -> None:
        """Stop the current shooting period."""
        self.timing.trigger_emergency_stop()
        # Match logic continues (scores remain recorded)

    def pause_match(self) -> None:
        """Pause the current shooting period."""
        self.timing.pause()

    def resume_match(self) -> None:
        """Resume the paused shooting period."""
        self.timing.resume()

    def add_arrow_score(self, score_value: str) -> bool:
        """
        Add an arrow score (only if match logic is enabled).
        Returns True if the arrow was accepted, False otherwise.
        """
        if not self.match_logic:
            return False
        self.match_logic.add_arrow_score(score_value)
        return True

    def undo_arrow(self) -> bool:
        """Remove the last arrow score (only if match logic is enabled)."""
        if not self.match_logic:
            return False
        return self.match_logic.undo_last_arrow()

    def finalize_current_end(self) -> bool:
        """
        Complete the current end and move to the next (if match logic is enabled).
        Returns True if the match continues, False if the match is complete.
        """
        if not self.match_logic:
            return True
        return self.match_logic.finalize_end()

    def advance_to_next_set(self) -> bool:
        """Advance to the next set (set-play mode only)."""
        if not self.match_logic:
            return False
        return self.match_logic.advance_set()

    def get_full_state(self) -> Dict[str, Any]:
        """Get the complete match state including timing and scoring."""
        timing_state = self.timing.build_state_update()

        result = {
            "config": {
                "event_type": self.config.event_type,
                "round_type": self.config.round_type,
                "match_logic_enabled": self.config.match_logic_enabled,
            },
            "timing": timing_state,
        }

        if self.match_logic:
            result["match"] = self.match_logic.get_match_state()

        return result
