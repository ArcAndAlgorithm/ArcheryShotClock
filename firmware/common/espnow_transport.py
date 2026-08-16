from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EspNowPacket:
    protocol_version: int = 1
    session_id: str = "default-session"
    message_type: str = "STATE_UPDATE"
    source_role: str = "controller"
    unit_id: str = "controller-01"
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        packet = {
            "protocol_version": self.protocol_version,
            "session_id": self.session_id,
            "message_type": self.message_type,
            "source_role": self.source_role,
            "unit_id": self.unit_id,
        }
        packet.update(self.payload)
        return packet


class EspNowTransport:
    def __init__(self) -> None:
        self.received: List[Dict[str, Any]] = []

    def send_state(self, session_id: str, unit_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        packet = EspNowPacket(
            session_id=session_id,
            message_type="STATE_UPDATE",
            source_role="controller",
            unit_id=unit_id,
            payload=payload,
        )
        self.received.append(packet.to_dict())
        return packet.to_dict()

    def send_signal(self, session_id: str, unit_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        packet = EspNowPacket(
            session_id=session_id,
            message_type="SIGNAL_EVENT",
            source_role="buzzer",
            unit_id=unit_id,
            payload=payload,
        )
        self.received.append(packet.to_dict())
        return packet.to_dict()

    def receive_last(self) -> Dict[str, Any]:
        if not self.received:
            return {}
        return self.received[-1]
