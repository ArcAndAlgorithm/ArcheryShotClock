#pragma once

#include <cstdint>
#include <cstring>

namespace archery {

// High-level match session configuration.
// Defines the event type, round type, and scoring rules.

struct SessionConfig {
    char event_type[32] = "INDIVIDUAL";  // INDIVIDUAL, TEAM, MIXED_TEAM
    char round_type[32] = "QUALIFICATION";  // QUALIFICATION, MATCH_PLAY, FINALS
    bool match_logic_enabled = false;
    char scoring_mode[32] = "CUMULATIVE";  // CUMULATIVE or SET_PLAY
    uint8_t arrows_per_end = 6;
    uint8_t total_ends = 12;
    uint16_t per_arrow_time_ms = 30000;  // in milliseconds
};

// Simplified end score tracking for the firmware.
// Holds up to 6 arrow scores per end.

class EndScoreTracker {
 public:
    static constexpr int kMaxArrowsPerEnd = 6;

    EndScoreTracker() : end_number_(0), arrow_count_(0) {}

    void set_end_number(uint8_t end_num) { end_number_ = end_num; }

    uint8_t end_number() const { return end_number_; }

    // Add an arrow score (0-10, or special values 'X', 'M').
    // For firmware simplicity, we store the numeric value.
    void add_arrow(uint8_t score) {
        if (arrow_count_ < kMaxArrowsPerEnd) {
            arrow_scores_[arrow_count_] = score;
            arrow_count_++;
        }
    }

    uint8_t arrow_count() const { return arrow_count_; }

    bool is_complete(uint8_t arrows_per_end) const {
        return arrow_count_ >= arrows_per_end;
    }

    uint16_t total_score() const {
        uint16_t sum = 0;
        for (uint8_t i = 0; i < arrow_count_; ++i) {
            sum += arrow_scores_[i];
        }
        return sum;
    }

    void reset() { arrow_count_ = 0; }

 private:
    uint8_t end_number_ = 0;
    uint8_t arrow_count_ = 0;
    uint8_t arrow_scores_[kMaxArrowsPerEnd] = {0};
};

// Firmware-level match session coordinator.
// Coordinates timing state and match/scoring state.

class MatchSessionController {
 public:
    MatchSessionController(const SessionConfig& config) : config_(config) {}

    // Start a new match.
    void start_match() {
        match_active_ = true;
        current_set_ = 1;
        current_end_ = 1;
        current_end_score_.set_end_number(current_end_);
    }

    // Finalize the current end and prepare for the next.
    // Returns true if the match continues, false if the match is complete.
    bool finalize_end() {
        if (!current_end_score_.is_complete(config_.arrows_per_end)) {
            return false;  // End not ready
        }

        if (current_end_ >= config_.total_ends) {
            match_active_ = false;
            return false;  // Match ends
        }

        current_end_++;
        current_end_score_.reset();
        current_end_score_.set_end_number(current_end_);
        return true;
    }

    // Add an arrow score to the current end.
    void add_arrow(uint8_t score) {
        current_end_score_.add_arrow(score);
    }

    bool match_active() const { return match_active_; }
    uint8_t current_end() const { return current_end_; }
    uint8_t current_set() const { return current_set_; }
    uint8_t arrows_in_end() const { return current_end_score_.arrow_count(); }
    uint16_t current_end_total() const { return current_end_score_.total_score(); }

 private:
    SessionConfig config_;
    bool match_active_ = false;
    uint8_t current_set_ = 0;
    uint8_t current_end_ = 0;
    EndScoreTracker current_end_score_;
};

}  // namespace archery
