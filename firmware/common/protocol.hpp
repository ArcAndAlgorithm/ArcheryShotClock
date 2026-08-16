#pragma once

#include <cstdint>

namespace archery {

enum class ProtocolVersion : uint16_t {
    V1 = 1,
};

enum class UnitRole : uint8_t {
    Controller = 0,
    Display = 1,
    Buzzer = 2,
};

enum class LightState : uint8_t {
    Off = 0,
    Red = 1,
    Green = 2,
    Yellow = 3,
};

enum class Phase : uint8_t {
    Idle = 0,
    Occupy = 1,
    Shooting = 2,
    Stopped = 3,
    Paused = 4,
    Scoring = 5,
};

struct StateUpdateMessage {
    uint16_t protocol_version = static_cast<uint16_t>(ProtocolVersion::V1);
    uint32_t timestamp_ms = 0;
    UnitRole source_role = UnitRole::Controller;
    char session_id[32] = "default-session";
    char unit_id[32] = "controller-01";
    LightState light = LightState::Off;
    Phase phase = Phase::Idle;
    bool active = false;
    bool paused = false;
    float time_remaining_seconds = 0.0f;
    int arrows_shot = 0;
    int arrows_per_end = 6;
    int end_number = 1;
    int set_number = 1;
};

struct SignalEvent {
    uint16_t protocol_version = static_cast<uint16_t>(ProtocolVersion::V1);
    uint32_t timestamp_ms = 0;
    char session_id[32] = "default-session";
    char unit_id[32] = "buzzer-01";
    char event_name[32] = "SIGNAL_START";
    int count = 1;
};

}  // namespace archery
