from __future__ import annotations

from dataclasses import dataclass, field

from firmware.common.protocol import StateUpdateMessage


@dataclass
class ControllerRuntime:
    session_id: str = "default-session"
    unit_id: str = "controller-01"
    active: bool = False
    paused: bool = False
    phase: str = "IDLE"
    light_state: str = "OFF"
    time_remaining_ms: int = 30000
    arrows_shot: int = 0
    arrows_per_end: int = 6
    end_number: int = 1
    set_number: int = 1
    yellow_warning_ms: int = 30000

    def start(self) -> None:
        self.active = True
        self.paused = False
        self.phase = "OCCUPY"
        self.light_state = "GREEN"
        self.time_remaining_ms = 30000
        self.arrows_shot = 0

    def tick(self, delta_seconds: float) -> None:
        if not self.active or self.paused:
            return

        self.time_remaining_ms = max(0, int(self.time_remaining_ms - delta_seconds * 1000))
        if self.time_remaining_ms <= self.yellow_warning_ms:
            self.light_state = "YELLOW"
        else:
            self.light_state = "GREEN"

        if self.time_remaining_ms <= 0:
            self.active = False
            self.phase = "STOPPED"
            self.light_state = "RED"

    def pause(self) -> None:
        if self.active and not self.paused:
            self.paused = True
            self.phase = "PAUSED"
            self.light_state = "YELLOW"

    def resume(self) -> None:
        if self.active and self.paused:
            self.paused = False
            self.phase = "OCCUPY"
            self.light_state = "GREEN"

    def trigger_emergency_stop(self) -> None:
        self.active = False
        self.paused = False
        self.phase = "STOPPED"
        self.light_state = "RED"

    def register_arrow_shot(self) -> None:
        if self.active:
            self.arrows_shot += 1
            if self.arrows_shot >= self.arrows_per_end:
                self.active = False
                self.phase = "SCORING"
                self.light_state = "RED"

    def build_state_update(self) -> dict:
        return StateUpdateMessage(
            session_id=self.session_id,
            unit_id=self.unit_id,
            device_role="controller",
            light_state=self.light_state,
            phase=self.phase,
            active=self.active,
            paused=self.paused,
            time_remaining_ms=self.time_remaining_ms,
            arrows_shot=self.arrows_shot,
            arrows_per_end=self.arrows_per_end,
            end_number=self.end_number,
            set_number=self.set_number,
        ).to_dict()
