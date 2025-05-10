
#include <stddef.h>
#include <stdint.h>
#include <esp_random.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <esp_wifi.h>
#include <esp_log.h>

#include "data.h"
#include "connection.h"

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


typedef struct __attribute__((packed)) {
    uint8_t batt_level;
} proto_0_data_t;

typedef struct __attribute__((packed)) {
    uint8_t batt_level;
    uint32_t timestamp;
} proto_1_data_t;

typedef struct __attribute__((packed)) {
    uint8_t batt_level;
    uint32_t timestamp;
    uint8_t temp;
    uint32_t press;
    uint8_t hum;
    float co;
} proto_2_data_t;

typedef struct __attribute__((packed)) {
    proto_2_data_t proto_2;
    float rms;
    float amp_x;
    float frec_x;
    float amp_y;
    float frec_y;
    float amp_z;
    float frec_z;
} proto_3_data_t;

typedef struct __attribute__((packed)) {
    proto_2_data_t proto_2;
    float acc_x[2000];
    float acc_y[2000];
    float acc_z[2000];
    float rgyr_x[2000];
    float rgyr_y[2000];
    float rgyr_z[2000];
} proto_4_data_t;

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


typedef void (*fill_func)(void*);

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

const size_t PROTOCOL_COUNT = sizeof(FILL_FUNCS) / sizeof(size_t);
const size_t HEADER_LENGTH = sizeof(packet_header_t);
const size_t HANDSHAKE_LENGTH = HEADER_LENGTH + sizeof(uint32_t);
const size_t MAX_PACKET_LENGTH = HEADER_LENGTH + sizeof(proto_4_data_t);

size_t get_packet_length(id_protocol_t id_protocol) {
    size_t data_length = id_protocol < PROTOCOL_COUNT? DATA_LENGTHS[id_protocol] : 0;
    return HEADER_LENGTH + data_length;
}

void gen_header(packet_header_t *header, uint16_t packet_id, const uint8_t mac_address[6],
                uint8_t transport_layer, id_protocol_t id_protocol, uint16_t packet_len) {
    header->packet_id = packet_id;
    memcpy(header->mac, mac_address, 6);
    header->transport_layer = transport_layer;
    header->id_protocol = id_protocol;
    header->packet_len = packet_len;
}


void gen_packet(void* packet_buf, uint16_t packet_id, const uint8_t mac_address[6],
                uint8_t transport_layer, id_protocol_t id_protocol ) {
    gen_header((packet_header_t*) packet_buf, packet_id, mac_address,
               transport_layer, id_protocol, get_packet_length(id_protocol));

    FILL_FUNCS[id_protocol](packet_buf + HEADER_LENGTH);

    ESP_LOGI(TAG, "Paquete generado con transport_layer: %hhu, id_protocol: %hhu", transport_layer, id_protocol);
}

void gen_handshake(void* packet_buf, const uint8_t mac_address[6], uint32_t id_device) {
    gen_header((packet_header_t*) packet_buf, 0, mac_address, TCP, HANDSHAKE, HANDSHAKE_LENGTH);
    *(uint32_t*)(packet_buf + HEADER_LENGTH) = id_device;
}
