#pragma once

#include "protocol.hpp"
#include "rgb_matrix_driver.hpp"

namespace archery {

// Display controller that renders the match state to an RGB matrix panel.
// Consumes StateUpdateMessage packets and converts them to visual output.

class DisplayController {
 public:
    // Initialize the display controller and hardware.
    bool init();

    // Update the display based on a controller state message.
    void on_state_update(const StateUpdateMessage& state);

    // Deinitialize the display.
    void deinit();

 private:
    StateUpdateMessage last_state_{};
    bool initialized_ = false;

    // Convert a LightState enum to an RGB color for the indicator light.
    static RgbColor light_state_to_color(LightState light);

    // Render the full display based on the current state.
    void render();
};

}  // namespace archery
