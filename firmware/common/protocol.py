from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


def _normalise_role(role: str) -> str:
    return str(role).strip().lower()


@dataclass
class StateUpdateMessage:
    session_id: str = "default-session"
    unit_id: str = "controller-01"
    device_role: str = "controller"
    light_state: str = "OFF"
    phase: str = "IDLE"
    active: bool = False
    paused: bool = False
    time_remaining_ms: int = 0
    arrows_shot: int = 0
    arrows_per_end: int = 6
    end_number: int = 1
    set_number: int = 1
    protocol_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol_version": self.protocol_version,
            "session_id": self.session_id,
            "unit_id": self.unit_id,
            "device_role": _normalise_role(self.device_role),
            "light_state": self.light_state,
            "phase": self.phase,
            "active": self.active,
            "paused": self.paused,
            "time_remaining_ms": self.time_remaining_ms,
            "arrows_shot": self.arrows_shot,
            "arrows_per_end": self.arrows_per_end,
            "end_number": self.end_number,
            "set_number": self.set_number,
        }


@dataclass
class SignalEvent:
    session_id: str = "default-session"
    unit_id: str = "buzzer-01"
    event_name: str = "SIGNAL_START"
    count: int = 1
    protocol_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol_version": self.protocol_version,
            "session_id": self.session_id,
            "unit_id": self.unit_id,
            "event_name": self.event_name,
            "count": self.count,
        }
