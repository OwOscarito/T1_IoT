
#include <esp_log.h>
#include <esp_sleep.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <nvs_flash.h>
#include <lwip/sockets.h>
#include <stdint.h>
#include <unistd.h>

#include "lwip/sockets.h"
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
    ESP_LOGI(TAG, "Conectado a WiFi!\n");

    struct sockaddr_in server_addr;
    get_server_address(&server_addr);

    uint8_t mac[6];
    get_mac_address(mac);

    uint32_t id_device = generate_device_id(mac);
    void* packet_buf = malloc(MAX_PACKET_LENGTH);
    uint16_t packet_id = 1;

    while (1) {
        db_config_t db_config = handshake(mac, id_device, &server_addr);
        ESP_LOGI(TAG, "db_config: %i %i", db_config.id_protocol, db_config.transport_layer);

        if (db_config.transport_layer == TCP) {
            int tcp_sock = gen_tcp_socket(&server_addr);
            
            gen_packet(packet_buf, packet_id, mac, TCP, db_config.id_protocol);

            packet_header_t* packet_header = packet_buf;
            send_tcp_data(tcp_sock, packet_buf, packet_header->packet_len);
            
            close(tcp_sock);
            
            esp_sleep_enable_timer_wakeup(60 * 1000000);
            esp_deep_sleep_start();

            packet_id++;

        } else if (db_config.transport_layer == UDP) {
            int udp_sock = gen_udp_socket();
            
            do {
                gen_packet(packet_buf, packet_id, mac, UDP, db_config.id_protocol);

                packet_header_t* packet = (packet_header_t*)packet_buf;
                send_udp_data(udp_sock, (void*)packet, packet->packet_len, &server_addr);

                packet_header_t recv_header;
                if (receive_udp_data(udp_sock, &recv_header, HEADER_LENGTH, &server_addr) == sizeof(recv_header)) {
                    db_config.transport_layer = recv_header.transport_layer;
                    db_config.id_protocol = recv_header.id_protocol;
                }

                packet_id++;
                sleep(1);
            } while (db_config.transport_layer == UDP);

            packet_id = 0;
            close(udp_sock);
        } else {
            sleep(5);
        }
    }
    free(packet_buf);
}

