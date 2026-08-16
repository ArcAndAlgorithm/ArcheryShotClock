from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BuzzerState:
    session_id: str = "default-session"
    unit_id: str = "buzzer-01"
    event_name: str = "SIGNAL_START"
    count: int = 1
    active: bool = False

    def apply_event(self, payload: dict) -> None:
        self.session_id = payload.get("session_id", self.session_id)
        self.unit_id = payload.get("unit_id", self.unit_id)
        self.event_name = payload.get("event_name", self.event_name)
        self.count = int(payload.get("count", self.count))
        self.active = bool(payload.get("active", False))

    def pattern(self) -> dict:
        return {
            "event_name": self.event_name,
            "count": self.count,
            "unit_id": self.unit_id,
            "session_id": self.session_id,
        }
