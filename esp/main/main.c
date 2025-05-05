
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <nvs_flash.h>
#include <lwip/sockets.h>

#include "wifi.h"
#include "connection.h"
#include "data.h"

static const char* TAG = "MAIN";

void nvs_init() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}


void app_main(void) {
    nvs_init();
    wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
    ESP_LOGI(TAG,"Conectado a WiFi!\n");

    while (1) {
        db_config_t db_conf;
        if (query_config(&db_conf)) { continue; }


        if (db_conf.transport_layer == TCP) {
            int tcp_sock = gen_tcp_socket();

            uint16_t packet_id = 1;
            packet_header_t* packet = (packet_header_t*) gen_packet(packet_id, TCP, 3);

            send_data(tcp_sock, (void*)packet, packet->packet_len);
            free(packet);
            close(tcp_sock);

        } else if (db_conf.transport_layer == UDP) {
            int udp_sock = gen_udp_socket();
            //send_data();
            close(udp_sock);
        }
    }
}

