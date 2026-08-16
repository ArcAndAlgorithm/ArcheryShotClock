#pragma once

#include "protocol.hpp"
#include "buzzer_driver.hpp"

namespace archery {

// Buzzer controller that plays audio patterns for signal events.
// Consumes SignalEvent packets and generates the corresponding tone sequences
// per Article 11.3 (signal patterns).

class BuzzerController {
 public:
    // Initialize the buzzer hardware and controller.
    bool init();

    // Handle a signal event and play the corresponding audio pattern.
    void on_signal_event(const SignalEvent& signal);

    // Deinitialize the buzzer.
    void deinit();

 private:
    SignalEvent last_signal_{};
    bool initialized_ = false;

    // Map a signal event name to the number of beeps and frequency per Article 11.3.
    struct SignalPattern {
        int num_beeps = 1;
        uint16_t frequency_hz = BuzzerDriver::kFrequencyHz;
        uint16_t beep_duration_ms = BuzzerDriver::kShortBeepMs;
    };

    SignalPattern get_signal_pattern(const char* event_name);
};

}  // namespace archery
