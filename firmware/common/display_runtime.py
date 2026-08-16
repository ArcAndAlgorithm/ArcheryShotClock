from __future__ import annotations


class DisplayRuntime:
    def __init__(self) -> None:
        self.state = {
            "light": "OFF",
            "phase": "IDLE",
            "active": False,
            "time_remaining_ms": 0,
            "score_display": False,
        }

    def consume_state(self, payload: dict) -> None:
        self.state["light"] = payload.get("light_state", "OFF")
        self.state["phase"] = payload.get("phase", "IDLE")
        self.state["active"] = bool(payload.get("active", False))
        self.state["time_remaining_ms"] = int(payload.get("time_remaining_ms", 0))
        self.state["score_display"] = bool(payload.get("score_display", False))

    def render(self) -> str:
        return (
            f"light={self.state['light']} phase={self.state['phase']} "
            f"active={self.state['active']} time={self.state['time_remaining_ms']}"
        )
