#pragma once

#include <cstdint>
#include <cstring>

namespace archery {

// RGB color representation for LED displays.
struct RgbColor {
    uint8_t r = 0;
    uint8_t g = 0;
    uint8_t b = 0;

    RgbColor() = default;
    RgbColor(uint8_t red, uint8_t green, uint8_t blue)
        : r(red), g(green), b(blue) {}

    static RgbColor Red() { return RgbColor(255, 0, 0); }
    static RgbColor Green() { return RgbColor(0, 255, 0); }
    static RgbColor Yellow() { return RgbColor(255, 255, 0); }
    static RgbColor Off() { return RgbColor(0, 0, 0); }
};

// Hardware abstraction for RGB dot-matrix display panels.
// Supports rendering a countdown clock and indicator light.
class RgbMatrixDriver {
 public:
    static constexpr int kMatrixWidth = 32;   // Typical 32-column panels
    static constexpr int kMatrixHeight = 8;   // Typical 8-row panels

    // Initialize the display hardware.
    // Returns true on success, false if initialization failed.
    static bool init();

    // Deinitialize the display.
    static void deinit();

    // Set the brightness level (0-255).
    static void set_brightness(uint8_t brightness);

    // Clear all pixels to black.
    static void clear();

    // Draw a solid rectangle of the given color.
    static void draw_rectangle(int x, int y, int width, int height,
                                const RgbColor& color);

    // Draw the time (in seconds) as a large numeric display.
    // Assumes a 32x8 matrix and renders centered, large digits.
    static void draw_time_seconds(float seconds);

    // Draw an indicator light in the top-right corner of the display.
    // Used to show the current phase (red/green/yellow).
    static void draw_indicator_light(const RgbColor& color);

    // Flush the framebuffer to the hardware (actually send pixels to the panel).
    static void flush();

    // Draw the full display state: time + indicator light.
    static void render_state(float time_seconds, const RgbColor& indicator_color);
};

}  // namespace archery
