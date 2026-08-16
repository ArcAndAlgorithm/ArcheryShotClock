from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LightState(str, Enum):
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    OFF = "OFF"


class Phase(str, Enum):
    IDLE = "IDLE"
    OCCUPY = "OCCUPY"
    SHOOTING = "SHOOTING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    SCORING = "SCORING"


@dataclass
class TimingConfig:
    arrow_time_seconds: float = 30.0
    arrows_per_end: int = 6
    occupy_time_seconds: float = 10.0
    yellow_warning_seconds: float = 30.0
    active_mode: str = "individual"


@dataclass
class TimingState:
    config: TimingConfig = field(default_factory=TimingConfig)
    active: bool = False
    paused: bool = False
    phase: Phase = Phase.IDLE
    light: LightState = LightState.OFF
    remaining_time: float = 0.0
    arrows_shot: int = 0
    end_number: int = 1
    set_number: int = 1
    last_event: Optional[str] = None

    def start(self) -> None:
        if not self.active:
            self.active = True
            self.paused = False
            self.phase = Phase.OCCUPY
            self.light = LightState.RED
            self.remaining_time = self.config.arrow_time_seconds * self.config.arrows_per_end
            self.last_event = "START"
            self._refresh_light_state()

    def tick(self, delta_seconds: float) -> None:
        if not self.active or self.paused:
            return

        self.remaining_time = max(0.0, self.remaining_time - delta_seconds)
        self._refresh_light_state()

        if self.remaining_time <= 0:
            self.active = False
            self.phase = Phase.STOPPED
            self.light = LightState.RED
            self.last_event = "TIME_EXPIRED"

    def pause(self) -> None:
        if self.active and not self.paused:
            self.paused = True
            self.phase = Phase.PAUSED
            self.light = LightState.YELLOW
            self.last_event = "PAUSE"

    def resume(self) -> None:
        if self.active and self.paused:
            self.paused = False
            self.phase = Phase.OCCUPY
            self.last_event = "RESUME"
            self._recalculate_resume_time()
            self._refresh_light_state()

    def stop(self) -> None:
        self.active = False
        self.paused = False
        self.phase = Phase.STOPPED
        self.light = LightState.RED
        self.last_event = "STOP"

    def register_arrow_shot(self) -> None:
        if self.active:
            self.arrows_shot += 1
            self.last_event = "ARROW_SHOT"
            if self.arrows_shot >= self.config.arrows_per_end:
                self.active = False
                self.phase = Phase.SCORING
                self.light = LightState.RED

    def _recalculate_resume_time(self) -> None:
        remaining_arrows = max(0, self.config.arrows_per_end - self.arrows_shot)
        recalculated = remaining_arrows * self.config.arrow_time_seconds
        if self.remaining_time > recalculated:
            return
        self.remaining_time = recalculated

    def _refresh_light_state(self) -> None:
        if not self.active:
            self.light = LightState.RED
            return

        if self.remaining_time <= self.config.yellow_warning_seconds:
            self.light = LightState.YELLOW
        else:
            self.light = LightState.GREEN

    def snapshot(self) -> dict:
        return {
            "active": self.active,
            "paused": self.paused,
            "phase": self.phase.value,
            "light": self.light.value,
            "remaining_time": round(self.remaining_time, 2),
            "arrows_shot": self.arrows_shot,
            "arrows_per_end": self.config.arrows_per_end,
            "end_number": self.end_number,
            "set_number": self.set_number,
            "last_event": self.last_event,
        }


def build_default_timing_state() -> TimingState:
    return TimingState(config=TimingConfig())
