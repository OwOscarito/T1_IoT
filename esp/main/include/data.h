#ifndef DATA_H
#define DATA_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    PROTOCOL0 = 0,
    PROTOCOL1 = 1,
    PROTOCOL2 = 2,
    PROTOCOL3 = 3,
    PROTOCOL4 = 4,
    HANDSHAKE = 5,
} id_protocol_t;


typedef struct __attribute__((packed)) {
    uint16_t packet_id;
    uint8_t mac[6];
    uint8_t transport_layer; // no usar los enums para estos valores porque el
    uint8_t id_protocol;     // tamaño de un enum es indefinido
    uint16_t packet_len;
} packet_header_t;

extern const size_t PROTOCOL_COUNT;
extern const size_t HEADER_LENGTH;
extern const size_t HANDSHAKE_LENGTH;
extern const size_t MAX_PACKET_LENGTH;

size_t get_packet_length(id_protocol_t id_protocol);

void gen_packet(void* packet_buf, uint16_t packet_id, const uint8_t mac_address[6],
                uint8_t transport_layer, id_protocol_t id_protocol);

void gen_handshake(void* packet_buf, const uint8_t mac_address[6], uint32_t id_device);

#endif // DATA_H
