
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <nvs_flash.h>
#include <lwip/sockets.h>

#include "wifi.h"
#include "data.h"

void nvs_init() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}

void socket_tcp(){
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    ESP_LOGI(TAG, "Conectando con servidor (%s:%u)", SERVER_IP, SERVER_PORT);

    // Crear un socket
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return;
    }

    // Conectar al servidor
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error al conectar");
        close(sock);
        return;
    }

    // Generar y enviar datos
    proto_2_data_t data;
    fill_proto_2_data(&data);

    send(sock, &data, sizeof data, 0);
    ESP_LOGI(TAG, "Datos enviados: (%hhu, %lu, %hhu, %lu, %hhu, %f)", 
             data.batt_level, data.timestamp, data.temp, data.press, data.hum, data.co);

    // Recibir datos de vuelta
    ssize_t data_len = recv(sock, &data, sizeof data, 0);
    if (data_len < sizeof data) {
        ESP_LOGE(TAG, "Volumen de datos recibidos incorrecto: %i (esperado: %u)", data_len, sizeof data);
        return;
    }
    ESP_LOGI(TAG, "Datos recibidos: (%hhu, %lu, %hhu, %lu, %hhu, %f)",
             data.batt_level, data.timestamp, data.temp, data.press, data.hum, data.co);
    
    // Cerrar el socket
    close(sock);
}

void app_main(void) {
    nvs_init();
    wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
    ESP_LOGI(TAG,"Conectado a WiFi!\n");
    socket_tcp();
}

