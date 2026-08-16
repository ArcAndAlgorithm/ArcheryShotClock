from __future__ import annotations

from firmware.common.controller_runtime import ControllerRuntime


class ControllerActions:
    def __init__(self, runtime: ControllerRuntime) -> None:
        self.runtime = runtime

    def start(self) -> str:
        self.runtime.start()
        return "STARTED"

    def stop(self) -> str:
        self.runtime.trigger_emergency_stop()
        return "STOPPED"

    def pause(self) -> str:
        self.runtime.pause()
        return "PAUSED"

    def resume(self) -> str:
        self.runtime.resume()
        return "RESUMED"

    def emergency_stop(self) -> str:
        self.runtime.trigger_emergency_stop()
        return "EMERGENCY_STOP"

    def add_arrow(self) -> str:
        self.runtime.register_arrow_shot()
        return "ARROW_REGISTERED"
