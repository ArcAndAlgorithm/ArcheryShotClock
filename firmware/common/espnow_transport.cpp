#include "espnow_transport.hpp"

#include <cstring>
#include <algorithm>

namespace archery {

// Marshalling helpers for wire protocol
// --

size_t EspNowTransport::marshal_state(const StateUpdateMessage& state, uint8_t* buffer) {
    uint8_t* ptr = buffer;
    
    // Header: packet type + version
    *ptr++ = kPacketTypeState;
    *reinterpret_cast<uint16_t*>(ptr) = state.protocol_version;
    ptr += 2;
    
    // Timestamp
    *reinterpret_cast<uint32_t*>(ptr) = state.timestamp_ms;
    ptr += 4;
    
    // Session ID (null-terminated string, max 32)
    std::strncpy(reinterpret_cast<char*>(ptr), state.session_id, 32);
    ptr += 32;
    
    // Unit ID (null-terminated string, max 32)
    std::strncpy(reinterpret_cast<char*>(ptr), state.unit_id, 32);
    ptr += 32;
    
    // Enums and simple fields
    *ptr++ = static_cast<uint8_t>(state.light);
    *ptr++ = static_cast<uint8_t>(state.phase);
    *ptr++ = state.active ? 1 : 0;
    *ptr++ = state.paused ? 1 : 0;
    
    // Time remaining (float)
    *reinterpret_cast<float*>(ptr) = state.time_remaining_seconds;
    ptr += 4;
    
    // Arrow counters
    *reinterpret_cast<int32_t*>(ptr) = state.arrows_shot;
    ptr += 4;
    *reinterpret_cast<int32_t*>(ptr) = state.arrows_per_end;
    ptr += 4;
    *reinterpret_cast<int32_t*>(ptr) = state.end_number;
    ptr += 4;
    *reinterpret_cast<int32_t*>(ptr) = state.set_number;
    ptr += 4;
    
    return ptr - buffer;
}

size_t EspNowTransport::marshal_signal(const SignalEvent& signal, uint8_t* buffer) {
    uint8_t* ptr = buffer;
    
    // Header: packet type + version
    *ptr++ = kPacketTypeSignal;
    *reinterpret_cast<uint16_t*>(ptr) = signal.protocol_version;
    ptr += 2;
    
    // Timestamp
    *reinterpret_cast<uint32_t*>(ptr) = signal.timestamp_ms;
    ptr += 4;
    
    // Session ID (null-terminated string, max 32)
    std::strncpy(reinterpret_cast<char*>(ptr), signal.session_id, 32);
    ptr += 32;
    
    // Unit ID (null-terminated string, max 32)
    std::strncpy(reinterpret_cast<char*>(ptr), signal.unit_id, 32);
    ptr += 32;
    
    // Event name (null-terminated string, max 32)
    std::strncpy(reinterpret_cast<char*>(ptr), signal.event_name, 32);
    ptr += 32;
    
    // Count
    *reinterpret_cast<int32_t*>(ptr) = signal.count;
    ptr += 4;
    
    return ptr - buffer;
}

bool EspNowTransport::unmarshal_state(const uint8_t* buffer, size_t size, StateUpdateMessage& out) {
    if (size < 3) {
        return false;  // Not enough for header
    }
    
    const uint8_t* ptr = buffer;
    uint8_t packet_type = *ptr++;
    if (packet_type != kPacketTypeState) {
        return false;
    }
    
    // Version check (optional for forward compatibility)
    uint16_t version = *reinterpret_cast<const uint16_t*>(ptr);
    ptr += 2;
    if (version != static_cast<uint16_t>(ProtocolVersion::V1)) {
        return false;  // Unsupported version
    }
    
    // Ensure we have enough data
    size_t expected_size = 1 + 2 + 4 + 32 + 32 + 1 + 1 + 1 + 1 + 4 + 4 + 4 + 4 + 4;
    if (size < expected_size) {
        return false;
    }
    
    // Timestamp
    out.timestamp_ms = *reinterpret_cast<const uint32_t*>(ptr);
    ptr += 4;
    
    // Session ID
    std::strncpy(out.session_id, reinterpret_cast<const char*>(ptr), 31);
    out.session_id[31] = '\0';
    ptr += 32;
    
    // Unit ID
    std::strncpy(out.unit_id, reinterpret_cast<const char*>(ptr), 31);
    out.unit_id[31] = '\0';
    ptr += 32;
    
    // Enums and simple fields
    out.light = static_cast<LightState>(*ptr++);
    out.phase = static_cast<Phase>(*ptr++);
    out.active = (*ptr++ != 0);
    out.paused = (*ptr++ != 0);
    
    // Time remaining
    out.time_remaining_seconds = *reinterpret_cast<const float*>(ptr);
    ptr += 4;
    
    // Arrow counters
    out.arrows_shot = *reinterpret_cast<const int32_t*>(ptr);
    ptr += 4;
    out.arrows_per_end = *reinterpret_cast<const int32_t*>(ptr);
    ptr += 4;
    out.end_number = *reinterpret_cast<const int32_t*>(ptr);
    ptr += 4;
    out.set_number = *reinterpret_cast<const int32_t*>(ptr);
    ptr += 4;
    
    return true;
}

bool EspNowTransport::unmarshal_signal(const uint8_t* buffer, size_t size, SignalEvent& out) {
    if (size < 3) {
        return false;  // Not enough for header
    }
    
    const uint8_t* ptr = buffer;
    uint8_t packet_type = *ptr++;
    if (packet_type != kPacketTypeSignal) {
        return false;
    }
    
    // Version check
    uint16_t version = *reinterpret_cast<const uint16_t*>(ptr);
    ptr += 2;
    if (version != static_cast<uint16_t>(ProtocolVersion::V1)) {
        return false;
    }
    
    // Ensure we have enough data
    size_t expected_size = 1 + 2 + 4 + 32 + 32 + 32 + 4;
    if (size < expected_size) {
        return false;
    }
    
    // Timestamp
    out.timestamp_ms = *reinterpret_cast<const uint32_t*>(ptr);
    ptr += 4;
    
    // Session ID
    std::strncpy(out.session_id, reinterpret_cast<const char*>(ptr), 31);
    out.session_id[31] = '\0';
    ptr += 32;
    
    // Unit ID
    std::strncpy(out.unit_id, reinterpret_cast<const char*>(ptr), 31);
    out.unit_id[31] = '\0';
    ptr += 32;
    
    // Event name
    std::strncpy(out.event_name, reinterpret_cast<const char*>(ptr), 31);
    out.event_name[31] = '\0';
    ptr += 32;
    
    // Count
    out.count = *reinterpret_cast<const int32_t*>(ptr);
    ptr += 4;
    
    return true;
}

// API implementations
// --

bool EspNowTransport::init() {
    // TODO: Call esp_now_init() and set up send/receive callbacks via ESP-IDF
    // For now, return a placeholder success indicator for testing.
    return true;
}

bool EspNowTransport::broadcast_state(const StateUpdateMessage& state) {
    uint8_t buffer[kMaxPayloadSize];
    size_t packet_size = marshal_state(state, buffer);
    
    if (packet_size > kMaxPayloadSize) {
        return false;
    }
    
    // TODO: Use esp_now_send() to broadcast buffer to kBroadcastMac
    // For now, return success to allow firmware compilation and testing.
    return true;
}

bool EspNowTransport::broadcast_signal(const SignalEvent& signal) {
    uint8_t buffer[kMaxPayloadSize];
    size_t packet_size = marshal_signal(signal, buffer);
    
    if (packet_size > kMaxPayloadSize) {
        return false;
    }
    
    // TODO: Use esp_now_send() to broadcast buffer to kBroadcastMac
    return true;
}

void EspNowTransport::process_inbox() {
    // TODO: Poll or dequeue received packets and invoke callbacks
    // For now, this is a placeholder for the receive handler integration.
}

}  // namespace archery
