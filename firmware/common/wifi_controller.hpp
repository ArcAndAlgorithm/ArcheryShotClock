#pragma once

#include <cstdint>

namespace archery {

// Wi-Fi configuration and setup for the controller unit.
// The controller runs as a Wi-Fi Access Point (AP) so the web UI
// and remote clients can connect for monitoring and control.

class WifiController {
 public:
    static constexpr const char* kDefaultSsid = "ArcheryTimer";
    static constexpr const char* kDefaultPassword = "12345678";
    static constexpr uint8_t kDefaultChannel = 6;

    // Initialize Wi-Fi in AP mode.
    // Returns true on success, false if initialization failed.
    static bool init_ap(const char* ssid = kDefaultSsid,
                        const char* password = kDefaultPassword,
                        uint8_t channel = kDefaultChannel);

    // Initialize Wi-Fi in STA (station) mode for device units that connect to a network.
    // Returns true on success, false otherwise.
    static bool init_sta(const char* ssid, const char* password);

    // Returns true if Wi-Fi is currently connected.
    static bool is_connected();

    // Get the local IP address (as a string like "192.168.4.1").
    static const char* get_ip_address();

    // Deinitialize Wi-Fi.
    static void deinit();
};

}  // namespace archery
