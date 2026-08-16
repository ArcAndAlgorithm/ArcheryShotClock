from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DisplayState:
    session_id: str = "default-session"
    unit_id: str = "display-01"
    active: bool = False
    paused: bool = False
    light: str = "OFF"
    phase: str = "IDLE"
    time_remaining_ms: int = 0
    arrows_shot: int = 0
    arrows_per_end: int = 6
    score_display: bool = False

    def apply_update(self, payload: dict) -> None:
        self.session_id = payload.get("session_id", self.session_id)
        self.active = bool(payload.get("active", False))
        self.paused = bool(payload.get("paused", False))
        self.light = payload.get("light_state", self.light)
        self.phase = payload.get("phase", self.phase)
        self.time_remaining_ms = int(payload.get("time_remaining_ms", self.time_remaining_ms))
        self.arrows_shot = int(payload.get("arrows_shot", self.arrows_shot))
        self.arrows_per_end = int(payload.get("arrows_per_end", self.arrows_per_end))
        self.score_display = bool(payload.get("score_display", self.score_display))

    def render_summary(self) -> str:
        return (
            f"{self.phase} | {self.light} | {self.time_remaining_ms / 1000:.1f}s | "
            f"arrows={self.arrows_shot}/{self.arrows_per_end}"
        )
