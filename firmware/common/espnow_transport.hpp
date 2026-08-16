#pragma once

#include <cstdint>
#include <cstring>
#include <functional>
#include <vector>

#include "protocol.hpp"

namespace archery {

// ESP-NOW transport packet wrapper for state and signal events.
// Marshals protocol messages into wire-safe byte payloads and routes
// incoming packets to subscribers.

class EspNowTransport {
 public:
    using StateCallback = std::function<void(const StateUpdateMessage&)>;
    using SignalCallback = std::function<void(const SignalEvent&)>;

    static constexpr size_t kMaxPayloadSize = 250;
    static constexpr uint8_t kBroadcastMac[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

    // Send a state update broadcast from the controller.
    bool broadcast_state(const StateUpdateMessage& state);

    // Send a signal event broadcast from the controller to buzzers.
    bool broadcast_signal(const SignalEvent& signal);

    // Register a callback for incoming state updates.
    void on_state_received(StateCallback callback) {
        state_callback_ = callback;
    }

    // Register a callback for incoming signal events.
    void on_signal_received(SignalCallback callback) {
        signal_callback_ = callback;
    }

    // Initialize the ESP-NOW subsystem (call once at startup).
    // Returns true on success, false if ESP-NOW could not be initialized.
    static bool init();

    // Process any pending received packets.
    // Typically called from the main loop or a task.
    void process_inbox();

 private:
    StateCallback state_callback_;
    SignalCallback signal_callback_;

    // Raw packet type marker.
    static constexpr uint8_t kPacketTypeState = 1;
    static constexpr uint8_t kPacketTypeSignal = 2;

    // Helper to marshal a StateUpdateMessage into a byte array.
    static size_t marshal_state(const StateUpdateMessage& state, uint8_t* buffer);

    // Helper to marshal a SignalEvent into a byte array.
    static size_t marshal_signal(const SignalEvent& signal, uint8_t* buffer);

    // Helper to unmarshal a byte array back into a StateUpdateMessage.
    static bool unmarshal_state(const uint8_t* buffer, size_t size, StateUpdateMessage& out);

    // Helper to unmarshal a byte array back into a SignalEvent.
    static bool unmarshal_signal(const uint8_t* buffer, size_t size, SignalEvent& out);
};

}  // namespace archery
