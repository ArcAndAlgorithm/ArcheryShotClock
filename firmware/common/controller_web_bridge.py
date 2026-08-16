from __future__ import annotations

from firmware.common.controller_runtime import ControllerRuntime
from firmware.common.webapi import WebControllerState


class ControllerWebBridge:
    def __init__(self, runtime: ControllerRuntime) -> None:
        self.runtime = runtime
        self.web_state = WebControllerState(
            active=runtime.active,
            paused=runtime.paused,
            phase=runtime.phase,
            light_state=runtime.light_state,
            time_remaining_ms=runtime.time_remaining_ms,
            arrows_shot=runtime.arrows_shot,
            arrows_per_end=runtime.arrows_per_end,
            session_id=runtime.session_id,
        )

    def sync(self) -> None:
        payload = self.runtime.build_state_update()
        self.web_state.active = payload["active"]
        self.web_state.paused = payload["paused"]
        self.web_state.phase = payload["phase"]
        self.web_state.light_state = payload["light_state"]
        self.web_state.time_remaining_ms = payload["time_remaining_ms"]
        self.web_state.arrows_shot = payload["arrows_shot"]
        self.web_state.arrows_per_end = payload["arrows_per_end"]
        self.web_state.session_id = payload["session_id"]
