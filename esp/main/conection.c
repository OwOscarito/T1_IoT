
#include <stdio.h>

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <nvs_flash.h>
#include <lwip/sockets.h>

#include "connection.h"
#include "wifi.h"

static const char* TAG = "CONNECTION";

int gen_tcp_socket() {
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    // Crear un socket
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return -1;
    }

    // Conectar al servidor
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error al conectar");
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

    // Crear un socket
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return -1;
    }

    // Conectar al servidor
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error al conectar con servidor.");
        close(sock);
        return -1;
    }

    return sock;
}

ssize_t send_data(int sock, void *data, ssize_t data_len) {
    // Enviar datos al servidor
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


