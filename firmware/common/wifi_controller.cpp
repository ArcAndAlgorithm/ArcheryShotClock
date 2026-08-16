#include "wifi_controller.hpp"

#include <cstring>

namespace archery {

namespace {
    char g_ip_address[16] = "192.168.4.1";  // Default AP mode IP
    bool g_initialized = false;
    bool g_connected = false;
}  // namespace

// --
// Wi-Fi initialization and management
// --

bool WifiController::init_ap(const char* ssid,
                              const char* password,
                              uint8_t channel) {
    if (g_initialized) {
        return true;  // Already initialized
    }

    // TODO: Call ESP-IDF functions:
    //   esp_netif_create_default_wifi_ap()
    //   wifi_config_t cfg = {
    //       .ap = {
    //           .ssid = "ArcheryTimer",
    //           .ssid_len = sizeof("ArcheryTimer") - 1,
    //           .channel = 6,
    //           .password = "12345678",
    //           .authmode = WIFI_AUTH_WPA2_PSK,
    //           .max_connection = 4,
    //       }
    //   };
    //   esp_wifi_set_mode(WIFI_MODE_AP)
    //   esp_wifi_set_config(WIFI_IF_AP, &cfg)
    //   esp_wifi_start()

    g_initialized = true;
    g_connected = true;
    std::strncpy(g_ip_address, "192.168.4.1", sizeof(g_ip_address) - 1);
    return true;
}

bool WifiController::init_sta(const char* ssid, const char* password) {
    if (g_initialized) {
        return true;
    }

    // TODO: Call ESP-IDF functions:
    //   esp_netif_create_default_wifi_sta()
    //   wifi_config_t cfg = {
    //       .sta = {
    //           .ssid = "...",
    //           .password = "...",
    //       }
    //   };
    //   esp_wifi_set_mode(WIFI_MODE_STA)
    //   esp_wifi_set_config(WIFI_IF_STA, &cfg)
    //   esp_wifi_start()
    //   esp_wifi_connect()

    g_initialized = true;
    g_connected = false;  // Will be set to true once connected
    return true;
}

bool WifiController::is_connected() {
    return g_initialized && g_connected;
}

const char* WifiController::get_ip_address() {
    return g_ip_address;
}

void WifiController::deinit() {
    // TODO: Call esp_wifi_stop() and esp_wifi_deinit()
    g_initialized = false;
    g_connected = false;
}

}  // namespace archery
