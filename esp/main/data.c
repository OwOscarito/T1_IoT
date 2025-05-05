
#include <stdint.h>
#include <esp_random.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <esp_wifi.h>
#include <esp_log.h>

#include "data.h"

static const char* TAG = "DATA";

float uniform_0_to_1() {
    return esp_random() / (float)UINT32_MAX;
}

float random_float(float min, float max) {
    return min + (max - min) * uniform_0_to_1();
}

void random_float_vector(float *vector, uint32_t len, float min, float max) {
    for (uint32_t i = 0; i < len; i++) {
        *(vector+i) = random_float(min, max);
    }
}

uint32_t random_int(uint32_t min, uint32_t max) {
    return min + esp_random() % (max - min + 1);
}

void fill_proto_0_data(void* buf) {
    proto_0_data_t *data = (proto_0_data_t*) buf;
    data->batt_level = random_int(1, 100);
}

void fill_proto_1_data(void* buf) {
    proto_1_data_t *data = (proto_1_data_t*) buf;
    data->batt_level = (uint8_t) random_int(1, 100);
    data->timestamp = time(NULL);
}

void fill_proto_2_data(void* buf) {
    proto_2_data_t *data = (proto_2_data_t*) buf;

    data->batt_level = (uint8_t) random_int(1, 100);
    data->timestamp = time(NULL);
    data->temp = random_int(5, 30);
    data->press = random_int(1000, 1200);
    data->hum = random_int(30, 80);
    data->co = random_float(30.0, 200.0);
}

void fill_proto_3_data(void* buf) {
    fill_proto_2_data(buf);
    proto_3_data_t *data = (proto_3_data_t*) buf;

    data->amp_x = random_float(0.0059, 0.12);
    data->frec_x = random_float(29.0, 31.0);
    data->amp_y = random_float(0.0041, 0.11);
    data->frec_y = random_float(59.0, 61.0);
    data->amp_z = random_float(0.008, 0.15);
    data->frec_z = random_float(89.0, 91.0);
    data->rms = sqrtf(powf(data->amp_x, 2) + powf(data->amp_y, 2) + powf(data->amp_z, 2));
}

void fill_proto_4_data(void* buf) {
    fill_proto_2_data(buf);
    proto_4_data_t *data = (proto_4_data_t*) buf;

    random_float_vector(data->acc_x, 6000, -16.0, 16.0);
    random_float_vector(data->rgyr_x, 6000, -1000.0, 1000.0);
}

const size_t DATA_LENGTHS[] = {
    sizeof(proto_0_data_t),
    sizeof(proto_1_data_t),
    sizeof(proto_2_data_t),
    sizeof(proto_3_data_t),
    sizeof(proto_4_data_t),
};

const fill_func FILL_FUNCS[] = {
    fill_proto_0_data,
    fill_proto_1_data,
    fill_proto_2_data,
    fill_proto_3_data,
    fill_proto_4_data,
};

const size_t PROTO_NUM = sizeof(DATA_LENGTHS) / sizeof(size_t);

void gen_header(
    packet_header_t *header, uint16_t packet_id,
    uint8_t transport_layer, uint8_t id_protocol, uint16_t packet_len
) {
    header->packet_id = packet_id;
    esp_wifi_get_mac(WIFI_IF_STA, header->mac);
    header->transport_layer = transport_layer;
    header->id_protocol = id_protocol;
    header->packet_len = packet_len;
}

void* gen_packet(uint16_t packet_id, uint8_t transport_layer, uint8_t id_protocol) {
    if (id_protocol >= PROTO_NUM) {
        ESP_LOGE(TAG, "Se intentó generar un paquere con un protocolo invalido (%hhu).", id_protocol);
        return NULL;
    }

    size_t data_len = DATA_LENGTHS[id_protocol];
    size_t header_len = sizeof(packet_header_t);
    size_t packet_len = header_len + data_len;

    uint8_t *buf = malloc(packet_len);

    gen_header((packet_header_t*) buf, packet_id, transport_layer, packet_id, packet_len);

    FILL_FUNCS[id_protocol](buf + header_len);
    
    return buf;
}
