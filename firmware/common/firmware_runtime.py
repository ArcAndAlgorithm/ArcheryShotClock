from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from firmware.common.broadcast import BroadcastTransport
from firmware.common.controller_runtime import ControllerRuntime
from firmware.common.display_state import DisplayState
from firmware.common.buzzer_state import BuzzerState


@dataclass
class FirmwareRuntime:
    controller: Optional[ControllerRuntime] = None
    transport: Optional[BroadcastTransport] = None
    display: Optional[DisplayState] = None
    buzzer: Optional[BuzzerState] = None

    def __post_init__(self) -> None:
        if self.controller is None:
            self.controller = ControllerRuntime()
        if self.transport is None:
            self.transport = BroadcastTransport()
        if self.display is None:
            self.display = DisplayState()
        if self.buzzer is None:
            self.buzzer = BuzzerState()

        self.transport.subscribe(self._on_state_message)
        self.transport.subscribe(self._on_signal_message)

    def tick(self, delta_seconds: float) -> None:
        if self.controller is not None:
            self.controller.tick(delta_seconds)
            self.transport.publish_state(self.controller.build_state_update())

    def _on_state_message(self, payload: Dict[str, Any]) -> None:
        if payload.get("message_type") == "STATE_UPDATE" and self.display is not None:
            self.display.apply_update(payload)

    def _on_signal_message(self, payload: Dict[str, Any]) -> None:
        if payload.get("message_type") == "SIGNAL_EVENT" and self.buzzer is not None:
            self.buzzer.apply_event(payload)

    def trigger_emergency(self) -> None:
        if self.controller is not None:
            self.controller.trigger_emergency_stop()
            self.transport.publish_state(self.controller.build_state_update())

    def start_match(self) -> None:
        if self.controller is not None:
            self.controller.start()
            self.transport.publish_state(self.controller.build_state_update())
