#include <algorithm>
#include <cstdio>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "../common/protocol.hpp"
#include "../common/espnow_transport.hpp"
#include "../common/wifi_controller.hpp"
#include "../common/match_session_controller.hpp"

namespace {

constexpr float kDefaultPeriodSeconds = 30.0f;

struct ControllerDevice {
    archery::StateUpdateMessage state{};
    float remaining_seconds = kDefaultPeriodSeconds;
    bool running = false;
    bool paused = false;

    void start() {
        running = true;
        paused = false;
        remaining_seconds = kDefaultPeriodSeconds;

        state.protocol_version = static_cast<uint16_t>(archery::ProtocolVersion::V1);
        state.timestamp_ms = 0;
        state.source_role = archery::UnitRole::Controller;
        std::snprintf(state.session_id, sizeof(state.session_id), "demo-session");
        std::snprintf(state.unit_id, sizeof(state.unit_id), "controller-01");
        state.phase = archery::Phase::Occupy;
        state.light = archery::LightState::Green;
        state.active = true;
        state.paused = false;
        state.time_remaining_seconds = remaining_seconds;
        state.arrows_shot = 0;
        state.arrows_per_end = 6;
        state.end_number = 1;
        state.set_number = 1;
    }

    void tick(float delta_seconds) {
        if (!running || paused) {
            return;
        }

        remaining_seconds = std::max(0.0f, remaining_seconds - delta_seconds);
        state.time_remaining_seconds = remaining_seconds;
        state.active = true;
        state.paused = false;

        if (remaining_seconds <= 0.0f) {
            running = false;
            state.phase = archery::Phase::Stopped;
            state.light = archery::LightState::Red;
            state.active = false;
            state.time_remaining_seconds = 0.0f;
            return;
        }

        if (remaining_seconds <= 30.0f) {
            state.phase = archery::Phase::Shooting;
            state.light = archery::LightState::Yellow;
        } else {
            state.phase = archery::Phase::Occupy;
            state.light = archery::LightState::Green;
        }
    }

    void pause() {
        if (!running || paused) {
            return;
        }

        paused = true;
        state.paused = true;
        state.phase = archery::Phase::Paused;
        state.light = archery::LightState::Yellow;
    }

    void resume() {
        if (!running || !paused) {
            return;
        }

        paused = false;
        state.paused = false;
        state.phase = archery::Phase::Shooting;
        state.light = archery::LightState::Green;
    }

    void stop() {
        running = false;
        paused = false;
        state.active = false;
        state.paused = false;
        state.phase = archery::Phase::Stopped;
        state.light = archery::LightState::Red;
        state.time_remaining_seconds = remaining_seconds;
    }
};

}  // namespace

extern "C" void app_main(void) {
    // Initialize Wi-Fi in AP mode
    if (!archery::WifiController::init_ap()) {
        std::printf("ERROR: Wi-Fi AP mode initialization failed\n");
        return;
    }
    std::printf("Wi-Fi AP mode initialized at %s\n", archery::WifiController::get_ip_address());

    // Initialize ESP-NOW transport
    if (!archery::EspNowTransport::init()) {
        std::printf("ERROR: ESP-NOW initialization failed\n");
        return;
    }
    std::printf("ESP-NOW transport initialized\n");

    ControllerDevice controller;
    archery::EspNowTransport transport;
    controller.start();

    for (int i = 0; i < 3; ++i) {
        controller.tick(5.0f);

        // Broadcast the current state
        transport.broadcast_state(controller.state);

        std::printf(
            "controller: phase=%d light=%d active=%d remaining=%.1f\n",
            static_cast<int>(controller.state.phase),
            static_cast<int>(controller.state.light),
            controller.state.active,
            controller.state.time_remaining_seconds);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    controller.pause();
    std::printf("controller: paused -> phase=%d light=%d\n",
                static_cast<int>(controller.state.phase),
                static_cast<int>(controller.state.light));

    controller.resume();
    std::printf("controller: resumed -> phase=%d light=%d\n",
                static_cast<int>(controller.state.phase),
                static_cast<int>(controller.state.light));

    controller.stop();
    std::printf("controller: stopped -> phase=%d light=%d\n",
                static_cast<int>(controller.state.phase),
                static_cast<int>(controller.state.light));
}
