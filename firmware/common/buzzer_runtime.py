from __future__ import annotations

from firmware.common.protocol import SignalEvent


class BuzzerRuntime:
    SIGNALS = {
        "SIGNAL_OCCUPY_LINE": 2,
        "SIGNAL_START": 1,
        "SIGNAL_WARNING": 1,
        "SIGNAL_STOP": 2,
        "SIGNAL_SCORING": 3,
        "SIGNAL_EMERGENCY": 5,
        "SIGNAL_RESUME": 1,
    }

    def play_signal(self, signal_name: str, count: int = 0) -> dict:
        # If count is not explicitly provided (0), use the signal-specific default
        event_count = count if count > 0 else self.SIGNALS.get(signal_name, 1)
        return SignalEvent(
            session_id="default-session",
            unit_id="buzzer-01",
            event_name=signal_name,
            count=event_count,
        ).to_dict()
