from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class BroadcastMessage:
    message_type: str
    payload: Dict[str, Any]
    protocol_version: int = 1

    def __post_init__(self) -> None:
        self.payload.setdefault("protocol_version", self.protocol_version)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_type": self.message_type,
            "protocol_version": self.protocol_version,
            **self.payload,
        }


class BroadcastTransport:
    def __init__(self) -> None:
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        self._listeners.append(listener)

    def publish_state(self, payload: Dict[str, Any]) -> None:
        message = BroadcastMessage("STATE_UPDATE", payload)
        self._dispatch(message)

    def publish_signal(self, payload: Dict[str, Any]) -> None:
        message = BroadcastMessage("SIGNAL_EVENT", payload)
        self._dispatch(message)

    def _dispatch(self, message: BroadcastMessage) -> None:
        data = message.to_dict()
        for listener in self._listeners:
            listener(data)


class BroadcastChannelFactory:
    @staticmethod
    def make() -> BroadcastTransport:
        return BroadcastTransport()
