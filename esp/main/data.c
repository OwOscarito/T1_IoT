
#include <stdint.h>
#include <esp_random.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "data.h"

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

void fill_proto_0_data(proto_0_data_t *data) {
    data->batt_level = random_int(1, 100);
}

void fill_proto_1_data(proto_1_data_t *data) {
    data->batt_level = (uint8_t) random_int(1, 100);
    data->timestamp = time(NULL);
}

void fill_proto_2_data(proto_2_data_t *data) {
    data->batt_level = (uint8_t) random_int(1, 100);
    data->timestamp = time(NULL);
    data->temp = random_int(5, 30);
    data->press = random_int(1000, 1200);
    data->hum = random_int(30, 80);
    data->co = random_float(30.0, 200.0);
}

void fill_proto_3_data(proto_3_data_t *data) {
    fill_proto_2_data(&data->proto_2);
    data->amp_x = random_float(0.0059, 0.12);
    data->frec_x = random_float(29.0, 31.0);
    data->amp_y = random_float(0.0041, 0.11);
    data->frec_y = random_float(59.0, 61.0);
    data->amp_z = random_float(0.008, 0.15);
    data->frec_z = random_float(89.0, 91.0);
    data->rms = sqrtf(powf(data->amp_x, 2) + powf(data->amp_y, 2) + powf(data->amp_z, 2));
}

void fill_proto_4_data(proto_4_data_t *data) {
    fill_proto_2_data(&data->proto_2);
    random_float_vector(data->acc_x, 6000, -16.0, 16.0);
    random_float_vector(data->rgyr_x, 6000, -1000.0, 1000.0);
}

