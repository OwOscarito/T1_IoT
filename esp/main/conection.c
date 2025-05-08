
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <nvs_flash.h>
#include <lwip/sockets.h>
#include <esp_mac.h>
#include <esp_log.h>
#include <stdlib.h>
#include <sys/types.h>

#include "connection.h"
#include "data.h"
#include "wifi.h"

static const char* TAG = "CONNECTION";

void get_mac_address(uint8_t mac[6]) {
    ESP_ERROR_CHECK(esp_efuse_mac_get_default(mac));

    ESP_LOGI(TAG, "MAC address: %02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

uint32_t generate_device_id(const uint8_t mac[6]) {
    return (mac[0] ^ mac[3]) | ((mac[1] ^ mac[4]) << 8) | ((mac[2] ^ mac[5]) << 16);
}

int gen_tcp_socket() {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);

    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr) != 1) {
        ESP_LOGE(TAG, "Dirección invalida: %s", SERVER_IP);
        return -1;
    }

    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al creat socket");
        return -1;
    }

    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error conectando socket a: %s:%d", SERVER_IP, SERVER_PORT);
        close(sock);
        return -1;
    }

    return sock;
}

int gen_udp_socket(){
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return -1;
    }

    return sock;
}

ssize_t send_data(int sock, const void *data, ssize_t data_len) {
    ssize_t sent_len = send(sock, data, data_len, 0);
    if (sent_len <= 0) {
        ESP_LOGE(TAG, "Error al enviar datos.");
    } else {
        ESP_LOGI(TAG, "Datos enviados: %i bytes.", sent_len);
    }
    return sent_len;
}

ssize_t receive_data(int sock, void *buf, ssize_t buf_len) {
    ssize_t recv_len = recv(sock, buf, buf_len, 0);
    if (recv_len <= 0) {
        ESP_LOGE(TAG, "Error al recibir datos.");
    } else {
        ESP_LOGI(TAG, "Datos recibidos: %i bytes.", recv_len);
    }
    return recv_len;
}

bool validate_db_config(db_config_t db_config) {
    return db_config.id_protocol >= PROTOCOL_COUNT 
        || db_config.transport_layer >= TRANSPORT_UNSPECIFIED;
}

db_config_t handshake(const uint8_t mac_address[6], uint32_t id_device) {
    int sock = gen_tcp_socket();

    uint8_t packet_buf[HANDSHAKE_LENGTH];
    gen_handshake(&packet_buf, mac_address, id_device);

    int err = send_data(sock, &packet_buf, sizeof(packet_buf));
    if (err < sizeof(packet_buf)) {
        ESP_LOGE(TAG, "Error al enviar datos de handshake");
        close(sock);
        return (db_config_t){ TRANSPORT_UNSPECIFIED, HANDSHAKE };
    }

    packet_header_t header;
    int recv = receive_data(sock, &header, HEADER_LENGTH); 
    
    db_config_t db_config = {header.transport_layer, header.id_protocol};

    if (recv != HEADER_LENGTH) {
        ESP_LOGE(TAG, "Largo incorrecta en respuesta del handshake (%i)", recv);
        close(sock);
        return (db_config_t){ TRANSPORT_UNSPECIFIED, HANDSHAKE };
    } else if (validate_db_config(db_config)) {
        ESP_LOGE(TAG, "Respuesta incorrecta en handshake (id_protocol: %hhu, transport_layer %hhu)", 
            db_config.id_protocol, db_config.transport_layer);
        close(sock);
        return (db_config_t){ TRANSPORT_UNSPECIFIED, HANDSHAKE };
    }

    close(sock);
    return db_config;
}

