#include "display_controller.hpp"

#include <cstdio>

namespace archery {

RgbColor DisplayController::light_state_to_color(LightState light) {
    switch (light) {
        case LightState::Red:
            return RgbColor::Red();
        case LightState::Green:
            return RgbColor::Green();
        case LightState::Yellow:
            return RgbColor::Yellow();
        case LightState::Off:
        default:
            return RgbColor::Off();
    }
}

bool DisplayController::init() {
    if (initialized_) {
        return true;
    }

    if (!RgbMatrixDriver::init()) {
        std::printf("ERROR: Display hardware initialization failed\n");
        return false;
    }

    RgbMatrixDriver::clear();
    RgbMatrixDriver::flush();
    initialized_ = true;
    std::printf("Display controller initialized\n");
    return true;
}

void DisplayController::on_state_update(const StateUpdateMessage& state) {
    last_state_ = state;
    render();
}

void DisplayController::render() {
    if (!initialized_) {
        return;
    }

    RgbColor indicator_color = light_state_to_color(last_state_.light);
    RgbMatrixDriver::render_state(last_state_.time_remaining_seconds, indicator_color);

    std::printf(
        "display_controller: rendered time=%.1fs light=%d phase=%d\n",
        last_state_.time_remaining_seconds,
        static_cast<int>(last_state_.light),
        static_cast<int>(last_state_.phase));
}

void DisplayController::deinit() {
    if (!initialized_) {
        return;
    }

    RgbMatrixDriver::deinit();
    initialized_ = false;
}

}  // namespace archery
