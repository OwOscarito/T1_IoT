
#include <stdint.h>

typedef struct __attribute__((packed)) {
    uint16_t id;
    uint8_t mac[6];
    uint8_t layer_4_proto;
    uint8_t data_proto;
    uint16_t len;
} packet_header_t;

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


void fill_proto_0_data(proto_0_data_t *data);
void fill_proto_1_data(proto_1_data_t *data);
void fill_proto_2_data(proto_2_data_t *data);
void fill_proto_3_data(proto_3_data_t *data);
void fill_proto_4_data(proto_4_data_t *data);

float random_float(float min, float max);

