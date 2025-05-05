#ifndef DATA_H
#define DATA_H

#include <stddef.h>
#include <stdint.h>

typedef struct __attribute__((packed)) {
    uint16_t packet_id;
    uint8_t mac[6];
    uint8_t transport_layer;
    uint8_t id_protocol;
    uint16_t packet_len;
} packet_header_t;

enum protocol_ids {
    PROTOCOL0 = 0,
    PROTOCOL1 = 1,
    PROTOCOL2 = 2,
    PROTOCOL3 = 3,
    PROTOCOL4 = 4,
    QUERY_PROTOCOL = 5,
};

extern const size_t PROTO_NUM;
extern const size_t HEADER_LENGTH;
extern const size_t MAX_PACKET_LENGTH;

size_t get_packet_length(uint8_t id_protocol);

void gen_packet(void* packet_buf, uint16_t packet_id, uint8_t transport_layer, uint8_t id_protocol);

#endif // DATA_H
