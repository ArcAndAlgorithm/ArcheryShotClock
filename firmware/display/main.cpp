#include <cstdio>

#include "../common/protocol.hpp"
#include "../common/espnow_transport.hpp"
#include "../common/wifi_controller.hpp"
#include "../common/display_controller.hpp"

namespace {

struct DisplayDevice {
    archery::StateUpdateMessage state{};
    bool score_display = false;

    void apply_state(const archery::StateUpdateMessage& incoming) {
        state = incoming;
        std::snprintf(state.unit_id, sizeof(state.unit_id), "display-01");
    }

    void render() const {
        std::printf(
            "display: session=%s phase=%d light=%d active=%d remaining=%.1f score_display=%d\n",
            state.session_id,
            static_cast<int>(state.phase),
            static_cast<int>(state.light),
            state.active,
            state.time_remaining_seconds,
            score_display ? 1 : 0);
    }
};

}  // namespace

extern "C" void app_main(void) {
    std::printf("Display unit initializing...\n");

    // Initialize ESP-NOW transport
    if (!archery::EspNowTransport::init()) {
        std::printf("ERROR: ESP-NOW initialization failed\n");
        return;
    }
    std::printf("ESP-NOW transport initialized for receive-only\n");

    // Initialize the display hardware and controller
    archery::DisplayController display_controller;
    if (!display_controller.init()) {
        std::printf("ERROR: Display controller initialization failed\n");
        return;
    }

    DisplayDevice display;

    // Set up a callback for when state updates arrive
    archery::EspNowTransport transport;
    transport.on_state_received([&display_controller, &display](const archery::StateUpdateMessage& state) {
        display.apply_state(state);
        display_controller.on_state_update(state);
    });

    // Render a demo state
    archery::StateUpdateMessage controller_state{};
    std::snprintf(controller_state.session_id, sizeof(controller_state.session_id), "demo-session");
    std::snprintf(controller_state.unit_id, sizeof(controller_state.unit_id), "controller-01");
    controller_state.protocol_version = static_cast<uint16_t>(archery::ProtocolVersion::V1);
    controller_state.source_role = archery::UnitRole::Controller;
    controller_state.phase = archery::Phase::Shooting;
    controller_state.light = archery::LightState::Yellow;
    controller_state.active = true;
    controller_state.time_remaining_seconds = 12.5f;
    controller_state.arrows_shot = 2;
    controller_state.arrows_per_end = 6;

    display.apply_state(controller_state);
    display_controller.on_state_update(controller_state);
}
