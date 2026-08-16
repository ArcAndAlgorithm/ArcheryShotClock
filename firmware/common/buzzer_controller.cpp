#include "buzzer_controller.hpp"

#include <cstring>
#include <cstdio>

namespace archery {

BuzzerController::SignalPattern BuzzerController::get_signal_pattern(const char* event_name) {
    // Map signal names to tone patterns per Article 11.3.1 and 11.3.3.

    if (std::strcmp(event_name, "SIGNAL_OCCUPY_LINE") == 0) {
        // Occupy line: 2 beeps
        return {2, BuzzerDriver::kFrequencyHz, BuzzerDriver::kShortBeepMs};
    }

    if (std::strcmp(event_name, "SIGNAL_START") == 0) {
        // Start shooting: 1 beep
        return {1, BuzzerDriver::kFrequencyHz, BuzzerDriver::kShortBeepMs};
    }

    if (std::strcmp(event_name, "SIGNAL_WARNING") == 0) {
        // 30s warning: 1 beep (lower frequency to distinguish)
        return {1, BuzzerDriver::kFrequencyWarningHz, BuzzerDriver::kShortBeepMs};
    }

    if (std::strcmp(event_name, "SIGNAL_STOP") == 0) {
        // Stop/finished: 2 beeps
        return {2, BuzzerDriver::kFrequencyHz, BuzzerDriver::kShortBeepMs};
    }

    if (std::strcmp(event_name, "SIGNAL_SCORING") == 0) {
        // Scoring may begin: 3 beeps
        return {3, BuzzerDriver::kFrequencyHz, BuzzerDriver::kShortBeepMs};
    }

    if (std::strcmp(event_name, "SIGNAL_EMERGENCY") == 0) {
        // Emergency stop: 5+ beeps at higher frequency
        return {5, 1200, BuzzerDriver::kLongBeepMs};
    }

    if (std::strcmp(event_name, "SIGNAL_RESUME") == 0) {
        // Resume after pause: 1 beep
        return {1, BuzzerDriver::kFrequencyHz, BuzzerDriver::kShortBeepMs};
    }

    // Default: single beep
    return {1, BuzzerDriver::kFrequencyHz, BuzzerDriver::kShortBeepMs};
}

bool BuzzerController::init() {
    if (initialized_) {
        return true;
    }

    if (!BuzzerDriver::init()) {
        std::printf("ERROR: Buzzer hardware initialization failed\n");
        return false;
    }

    initialized_ = true;
    std::printf("Buzzer controller initialized\n");
    return true;
}

void BuzzerController::on_signal_event(const SignalEvent& signal) {
    if (!initialized_) {
        return;
    }

    last_signal_ = signal;

    SignalPattern pattern = get_signal_pattern(signal.event_name);

    std::printf(
        "buzzer_controller: signal=%s beeps=%d freq=%d Hz\n",
        signal.event_name,
        pattern.num_beeps,
        pattern.frequency_hz);

    BuzzerDriver::play_signal_sequence(
        pattern.num_beeps,
        pattern.beep_duration_ms,
        BuzzerDriver::kGapMs,
        pattern.frequency_hz);
}

void BuzzerController::deinit() {
    if (!initialized_) {
        return;
    }

    BuzzerDriver::deinit();
    initialized_ = false;
}

}  // namespace archery
