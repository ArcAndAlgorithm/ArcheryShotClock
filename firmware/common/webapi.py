from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional

from firmware.common.controller_actions import ControllerActions
from firmware.common.controller_runtime import ControllerRuntime


@dataclass
class WebControllerState:
    active: bool = False
    paused: bool = False
    phase: str = "IDLE"
    light_state: str = "OFF"
    time_remaining_ms: int = 30000
    arrows_shot: int = 0
    arrows_per_end: int = 6
    session_id: str = "default-session"

    def to_dict(self) -> Dict[str, object]:
        return {
            "active": self.active,
            "paused": self.paused,
            "phase": self.phase,
            "light_state": self.light_state,
            "time_remaining_ms": self.time_remaining_ms,
            "arrows_shot": self.arrows_shot,
            "arrows_per_end": self.arrows_per_end,
            "session_id": self.session_id,
        }


class ArcheryRequestHandler(BaseHTTPRequestHandler):
    server_version = "ArcheryShotClock/0.1"
    _state: Optional[WebControllerState] = None
    _runtime: Optional[ControllerRuntime] = None
    _actions: Optional[ControllerActions] = None

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/state":
            payload = json.dumps(self._state.to_dict() if self._state else WebControllerState().to_dict()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/":
            with open("webui/index.html", "rb") as fh:
                content = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/app.js":
            with open("webui/app.js", "rb") as fh:
                content = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/start":
            if self._actions is not None:
                result = self._actions.start()
                self._state = WebControllerState(
                    active=self._runtime.active,
                    paused=self._runtime.paused,
                    phase=self._runtime.phase,
                    light_state=self._runtime.light_state,
                    time_remaining_ms=self._runtime.time_remaining_ms,
                    arrows_shot=self._runtime.arrows_shot,
                    arrows_per_end=self._runtime.arrows_per_end,
                    session_id=self._runtime.session_id,
                )
                self._send_json({"status": result})
                return

        if self.path == "/api/stop":
            if self._actions is not None:
                result = self._actions.stop()
                self._state = WebControllerState(
                    active=self._runtime.active,
                    paused=self._runtime.paused,
                    phase=self._runtime.phase,
                    light_state=self._runtime.light_state,
                    time_remaining_ms=self._runtime.time_remaining_ms,
                    arrows_shot=self._runtime.arrows_shot,
                    arrows_per_end=self._runtime.arrows_per_end,
                    session_id=self._runtime.session_id,
                )
                self._send_json({"status": result})
                return

        if self.path == "/api/pause":
            if self._actions is not None:
                result = self._actions.pause()
                self._state = WebControllerState(
                    active=self._runtime.active,
                    paused=self._runtime.paused,
                    phase=self._runtime.phase,
                    light_state=self._runtime.light_state,
                    time_remaining_ms=self._runtime.time_remaining_ms,
                    arrows_shot=self._runtime.arrows_shot,
                    arrows_per_end=self._runtime.arrows_per_end,
                    session_id=self._runtime.session_id,
                )
                self._send_json({"status": result})
                return

        if self.path == "/api/resume":
            if self._actions is not None:
                result = self._actions.resume()
                self._state = WebControllerState(
                    active=self._runtime.active,
                    paused=self._runtime.paused,
                    phase=self._runtime.phase,
                    light_state=self._runtime.light_state,
                    time_remaining_ms=self._runtime.time_remaining_ms,
                    arrows_shot=self._runtime.arrows_shot,
                    arrows_per_end=self._runtime.arrows_per_end,
                    session_id=self._runtime.session_id,
                )
                self._send_json({"status": result})
                return

        if self.path == "/api/emergency":
            if self._actions is not None:
                result = self._actions.emergency_stop()
                self._state = WebControllerState(
                    active=self._runtime.active,
                    paused=self._runtime.paused,
                    phase=self._runtime.phase,
                    light_state=self._runtime.light_state,
                    time_remaining_ms=self._runtime.time_remaining_ms,
                    arrows_shot=self._runtime.arrows_shot,
                    arrows_per_end=self._runtime.arrows_per_end,
                    session_id=self._runtime.session_id,
                )
                self._send_json({"status": result})
                return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, payload: Dict[str, str]) -> None:  # noqa: PLR0913
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_web_server(state: WebControllerState, host: str = "0.0.0.0", port: int = 8080, runtime: Optional[ControllerRuntime] = None) -> ThreadingHTTPServer:
    ArcheryRequestHandler._state = state
    ArcheryRequestHandler._runtime = runtime
    if runtime is not None:
        ArcheryRequestHandler._actions = ControllerActions(runtime)
    server = ThreadingHTTPServer((host, port), ArcheryRequestHandler)
    return server

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def run_web_server(state: WebControllerState, host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    ArcheryRequestHandler._state = state
    server = ThreadingHTTPServer((host, port), ArcheryRequestHandler)
    return server
