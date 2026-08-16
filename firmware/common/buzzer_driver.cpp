#include "buzzer_driver.hpp"

#include <cstdio>

namespace archery {

namespace {
    bool g_initialized = false;
    bool g_playing = false;
    uint16_t g_remaining_ms = 0;
}

bool BuzzerDriver::init() {
    if (g_initialized) {
        return true;
    }

    // TODO: Initialize PWM GPIO via ESP-IDF
    // Example:
    //   ledc_timer_config_t timer_conf = {...};
    //   ledc_timer_config(&timer_conf);
    //   ledc_channel_config_t channel_conf = {...};
    //   ledc_channel_config(&channel_conf);

    g_initialized = true;
    std::printf("Buzzer driver initialized\n");
    return true;
}

void BuzzerDriver::deinit() {
    if (!g_initialized) {
        return;
    }

    stop();
    // TODO: Disable PWM and free GPIO resources.
    g_initialized = false;
}

void BuzzerDriver::beep(uint16_t duration_ms, uint16_t frequency_hz) {
    if (!g_initialized) {
        return;
    }

    // TODO: Start PWM at the specified frequency.
    // This is typically a call to ledc_set_duty() + ledc_update_duty().
    // The actual duration would be handled by a timer interrupt or task.

    g_playing = true;
    g_remaining_ms = duration_ms;

    std::printf("buzzer: beep %d ms at %d Hz\n", duration_ms, frequency_hz);
}

void BuzzerDriver::play_signal_sequence(int num_beeps,
                                         uint16_t beep_duration_ms,
                                         uint16_t gap_ms,
                                         uint16_t frequency_hz) {
    if (!g_initialized || num_beeps <= 0) {
        return;
    }

    // For simplicity in this implementation, we log the sequence.
    // A real implementation would use a state machine or task to
    // alternate between playing beeps and gaps.

    std::printf("buzzer: signal sequence %d beeps, %d ms each, %d Hz\n",
                num_beeps, beep_duration_ms, frequency_hz);

    for (int i = 0; i < num_beeps; ++i) {
        beep(beep_duration_ms, frequency_hz);
        // TODO: Wait for gap_ms (actual timing handled by interrupt/task).
    }
}

void BuzzerDriver::stop() {
    if (!g_initialized) {
        return;
    }

    // TODO: Stop PWM output.
    g_playing = false;
    g_remaining_ms = 0;
    std::printf("buzzer: stopped\n");
}

bool BuzzerDriver::is_playing() {
    return g_playing;
}

}  // namespace archery
