#pragma once

#include <cstdint>

namespace archery {

// Audio tone and signal pattern generator.
// Produces the specific beep patterns required by Article 11.3.

class BuzzerDriver {
 public:
    // Frequency in Hz for standard buzzer signals.
    static constexpr uint16_t kFrequencyHz = 1000;
    static constexpr uint16_t kFrequencyWarningHz = 800;

    // Duration in milliseconds.
    static constexpr uint16_t kShortBeepMs = 200;
    static constexpr uint16_t kLongBeepMs = 500;
    static constexpr uint16_t kGapMs = 150;

    // Initialize the buzzer hardware (GPIO, PWM, etc.).
    // Returns true on success.
    static bool init();

    // Deinitialize the buzzer.
    static void deinit();

    // Play a single beep.
    static void beep(uint16_t duration_ms = kShortBeepMs,
                      uint16_t frequency_hz = kFrequencyHz);

    // Play a sequence of N beeps with gaps between them (Article 11.3).
    // Example: play_signal_sequence(2) produces a 2-beep "stop" signal.
    static void play_signal_sequence(int num_beeps,
                                      uint16_t beep_duration_ms = kShortBeepMs,
                                      uint16_t gap_ms = kGapMs,
                                      uint16_t frequency_hz = kFrequencyHz);

    // Stop any currently playing sound immediately.
    static void stop();

    // Get the current playback state (true if sound is playing).
    static bool is_playing();
};

}  // namespace archery
