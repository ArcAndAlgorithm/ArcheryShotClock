# ESP-NOW Protocol

This document is the initial protocol specification for the Archery Shot Clock project.
It is intentionally small and versioned so the controller, display nodes, and buzzer nodes
can evolve without breaking the real-time timing path.

## 1. Goals

- Keep lighting and countdown updates near-simultaneous across all paired display units.
- Use ESP-NOW broadcast as the primary control channel.
- Allow a controller to manage a session and a field of displays/buzzers without creating
  a per-unit peer list that scales poorly.
- Keep the protocol versioned so hardware mismatches fail safely instead of silently.

## 2. Transport

- Controller -> Units: ESP-NOW broadcast
- Unit -> Controller: low-rate unicast heartbeat, optional status replies
- Wi-Fi: controller-hosted web UI and session config on the same device

## 3. Message envelope

Every message includes:

```json
{
  "protocol_version": 1,
  "session_id": "demo-session",
  "message_type": "STATE_UPDATE",
  "source_role": "controller",
  "unit_id": "controller-01",
  "timestamp_ms": 123456789,
  "payload": {}
}
```

### Required fields

- `protocol_version`: integer, incremented for breaking protocol changes.
- `session_id`: logical session identifier to prevent cross-talk between matches.
- `message_type`: enumerated type such as `STATE_UPDATE`, `HEARTBEAT`, `PAIRING`, `EVENT`.
- `source_role`: controller, display, or buzzer.
- `unit_id`: unique per device within the current session.
- `timestamp_ms`: monotonically increasing controller/device time.
- `payload`: message-specific object.

## 4. State update payload

```json
{
  "message_type": "STATE_UPDATE",
  "payload": {
    "time_remaining_ms": 120000,
    "light_state": "GREEN",
    "active": true,
    "phase": "SHOOTING",
    "arrows_shot": 2,
    "arrows_per_end": 6,
    "end_number": 1,
    "set_number": 1,
    "score_display": false
  }
}
```

### Meaning

- `time_remaining_ms`: authoritative digital countdown remaining.
- `light_state`: one of `RED`, `GREEN`, `YELLOW`, `OFF`.
- `active`: whether the timer is currently running.
- `phase`: high-level mode state such as `IDLE`, `OCCUPY`, `SHOOTING`, `SCORING`, `PAUSED`.
- `arrows_shot`: count of arrows shot in the current end.
- `arrows_per_end`: expected end size for that mode.
- `end_number` and `set_number`: optional tracking for the current match.
- `score_display`: if true, the display should render score details instead of pure countdown.

## 5. Signal codes

Buzzer and PA units should consume event codes instead of raw audio streams.

```json
{
  "message_type": "EVENT",
  "payload": {
    "event": "SIGNAL_START",
    "count": 1,
    "repeat": false
  }
}
```

Supported events:

- `SIGNAL_OCCUPY_LINE`
- `SIGNAL_START`
- `SIGNAL_WARNING`
- `SIGNAL_STOP`
- `SIGNAL_SCORING`
- `SIGNAL_EMERGENCY`
- `SIGNAL_RESUME`

## 6. Pairing and heartbeats

Display and buzzer nodes should announce themselves and respond to pairing updates.
A simple pairing flow is:

- node broadcasts `HEARTBEAT` with a unit type and MAC address
- controller adds the node to the session when approved via the web UI
- controller stores `session_id`, node MAC, and role in a pairing table
- periodic heartbeats maintain connectivity and allow stale-state fallback on the display

## 7. Failure behaviour

If a node receives a message with an unsupported `protocol_version`, it should show a
firmware mismatch state rather than continuing with stale assumptions.

If a display node stops hearing broadcasts for a short timeout, it should degrade gracefully
by indicating a clear no-signal state instead of freezing the previous countdown.

## 8. Roadmap

This document is intentionally the first stable reference. The project will extend it with
more detailed payloads for scoring, end transitions, and multi-match operation once the core
clock and controller flow are validated.
