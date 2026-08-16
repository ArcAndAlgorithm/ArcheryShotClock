#include "rgb_matrix_driver.hpp"

#include <cstdio>
#include <algorithm>

namespace archery {

namespace {
    // Framebuffer: kMatrixWidth × kMatrixHeight array of RGB pixels.
    RgbColor g_framebuffer[RgbMatrixDriver::kMatrixWidth * RgbMatrixDriver::kMatrixHeight];
    bool g_initialized = false;
    uint8_t g_brightness = 255;

    // Get pixel at (x, y) in framebuffer.
    RgbColor* get_pixel(int x, int y) {
        if (x < 0 || x >= RgbMatrixDriver::kMatrixWidth ||
            y < 0 || y >= RgbMatrixDriver::kMatrixHeight) {
            return nullptr;
        }
        return &g_framebuffer[y * RgbMatrixDriver::kMatrixWidth + x];
    }

    // Simple 5x7 ASCII character font data (simplified for demo).
    // Each character is represented as a bitmap for rendering.
    struct CharBitmap {
        uint8_t width;
        uint8_t height;
        const uint8_t* data;  // Packed bitmap data
    };

    // Placeholder bitmap for digit '0' (5 pixels wide, 7 pixels tall).
    static constexpr uint8_t digit_0[] = {
        0b01110,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b01110,
    };

    // Placeholder bitmaps for digits 1-9 and colon (abbreviated for space).
    static constexpr uint8_t digit_1[] = {
        0b00100,
        0b01100,
        0b00100,
        0b00100,
        0b00100,
        0b00100,
        0b01110,
    };

    CharBitmap get_digit_bitmap(char digit) {
        if (digit == '0') return {5, 7, digit_0};
        if (digit == '1') return {5, 7, digit_1};
        return {5, 7, digit_0};  // Default fallback
    }

    // Draw a single character at position (x, y).
    void draw_char(int x, int y, char ch, const RgbColor& color) {
        CharBitmap bitmap = get_digit_bitmap(ch);
        for (int row = 0; row < bitmap.height; ++row) {
            uint8_t row_data = bitmap.data[row];
            for (int col = 0; col < bitmap.width; ++col) {
                if (row_data & (1 << (bitmap.width - 1 - col))) {
                    RgbColor* pixel = get_pixel(x + col, y + row);
                    if (pixel) {
                        *pixel = color;
                    }
                }
            }
        }
    }
}  // namespace

// --
// Public API implementations
// --

bool RgbMatrixDriver::init() {
    if (g_initialized) {
        return true;
    }

    // TODO: Initialize actual hardware via ESP-IDF GPIO or LED driver library.
    // Example:
    //   - gpio_config_t io_conf = {...};
    //   - gpio_config(&io_conf);
    //   - Or use esp_lcd or similar library for RGB panel control.

    std::memset(g_framebuffer, 0, sizeof(g_framebuffer));
    g_initialized = true;
    return true;
}

void RgbMatrixDriver::deinit() {
    if (!g_initialized) {
        return;
    }

    // TODO: Deinitialize GPIO or LED driver.
    clear();
    flush();
    g_initialized = false;
}

void RgbMatrixDriver::set_brightness(uint8_t brightness) {
    g_brightness = brightness;
    // TODO: Apply brightness via PWM or other hardware control.
}

void RgbMatrixDriver::clear() {
    std::memset(g_framebuffer, 0, sizeof(g_framebuffer));
}

void RgbMatrixDriver::draw_rectangle(int x, int y, int width, int height,
                                      const RgbColor& color) {
    for (int row = y; row < y + height && row < kMatrixHeight; ++row) {
        for (int col = x; col < x + width && col < kMatrixWidth; ++col) {
            RgbColor* pixel = get_pixel(col, row);
            if (pixel) {
                *pixel = color;
            }
        }
    }
}

void RgbMatrixDriver::draw_time_seconds(float seconds) {
    // Convert seconds to MM:SS format and render.
    int total_seconds = static_cast<int>(seconds);
    int minutes = total_seconds / 60;
    int secs = total_seconds % 60;

    char time_str[8];
    std::snprintf(time_str, sizeof(time_str), "%02d:%02d", minutes, secs);

    // Render the time string centered on the display (simplified to left-align for demo).
    int x_start = 2;
    int y_start = 1;
    for (int i = 0; time_str[i] != '\0' && i < 5; ++i) {
        draw_char(x_start + (i * 6), y_start, time_str[i], RgbColor::Green());
    }
}

void RgbMatrixDriver::draw_indicator_light(const RgbColor& color) {
    // Draw a small 4x4 square in the top-right corner.
    draw_rectangle(kMatrixWidth - 6, 1, 4, 4, color);
}

void RgbMatrixDriver::flush() {
    if (!g_initialized) {
        return;
    }

    // TODO: Send g_framebuffer contents to actual hardware.
    // This might involve:
    //   - DMA transfer to LED driver IC
    //   - GPIO bit-banging for panels without dedicated IC
    //   - I2C or SPI command sequence

    // For now, just log that we've rendered (for simulation/testing).
    std::printf("display: flushed framebuffer (%d pixels)\n",
                kMatrixWidth * kMatrixHeight);
}

void RgbMatrixDriver::render_state(float time_seconds, const RgbColor& indicator_color) {
    clear();
    draw_time_seconds(time_seconds);
    draw_indicator_light(indicator_color);
    flush();
}

}  // namespace archery
