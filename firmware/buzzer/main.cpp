#include <cstdio>

#include "../common/protocol.hpp"
#include "../common/espnow_transport.hpp"
#include "../common/wifi_controller.hpp"
#include "../common/buzzer_controller.hpp"

namespace {

struct BuzzerDevice {
    archery::SignalEvent last_signal{};

    void apply_signal(const archery::SignalEvent& incoming) {
        last_signal = incoming;
    }

    void play() const {
        std::printf(
            "buzzer: session=%s event=%s count=%d\n",
            last_signal.session_id,
            last_signal.event_name,
            last_signal.count);
    }
};

}  // namespace

extern "C" void app_main(void) {
    std::printf("Buzzer unit initializing...\n");

    // Initialize ESP-NOW transport for receive-only signal events
    if (!archery::EspNowTransport::init()) {
        std::printf("ERROR: ESP-NOW initialization failed\n");
        return;
    }
    std::printf("ESP-NOW transport initialized for signal events\n");

    // Initialize the buzzer hardware and controller
    archery::BuzzerController buzzer_controller;
    if (!buzzer_controller.init()) {
        std::printf("ERROR: Buzzer controller initialization failed\n");
        return;
    }

    BuzzerDevice buzzer;

    // Set up a callback for when signal events arrive
    archery::EspNowTransport transport;
    transport.on_signal_received([&buzzer_controller, &buzzer](const archery::SignalEvent& signal) {
        buzzer.apply_signal(signal);
        buzzer_controller.on_signal_event(signal);
    });

    archery::SignalEvent signal{};
    std::snprintf(signal.session_id, sizeof(signal.session_id), "demo-session");
    std::snprintf(signal.unit_id, sizeof(signal.unit_id), "buzzer-01");
    std::snprintf(signal.event_name, sizeof(signal.event_name), "SIGNAL_START");
    signal.count = 1;
    signal.protocol_version = static_cast<uint16_t>(archery::ProtocolVersion::V1);

    buzzer.apply_signal(signal);
    buzzer_controller.on_signal_event(signal);
}
