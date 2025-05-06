#ifndef CONNECTION_H
#define CONNECTION_H

#include <stdbool.h>
#include <stdint.h>
#include <socket.h>

#include "data.h"

enum TransportLayer{
    TCP = 0,
    UDP = 1,
    TRANSPORT_UNSPECIFIED = 2
};

typedef struct {
    enum TransportLayer transport_layer;
    id_protocol_t id_protocol;
} db_config_t;


void get_mac_address(uint8_t mac[6]);
uint32_t generate_device_id(const uint8_t mac[6]);

int gen_tcp_socket();
int gen_udp_socket();

ssize_t send_data(int sock, const void *data, ssize_t data_len);
ssize_t receive_data(int sock, void *buf, ssize_t buf_len);

bool validate_db_config(db_config_t db_config);
db_config_t handshake(const uint8_t mac_address[6], uint32_t id_device);

#endif // CONNECTION_H
