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
int get_server_address(struct sockaddr_in* server_addr);
uint32_t generate_device_id(const uint8_t mac[6]);

int gen_tcp_socket(const struct sockaddr_in* server_addr);
int gen_udp_socket();

ssize_t send_tcp_data(int sock, const void *data, size_t data_len);
ssize_t receive_tcp_data(int sock, void *buf, size_t buf_len);

ssize_t send_udp_data(int sock, const void *data, size_t data_len, const struct sockaddr_in *dest_addr);
ssize_t receive_udp_data(int sock, void *buf, size_t buf_len, struct sockaddr_in *src_addr);

bool validate_db_config(db_config_t db_config);
db_config_t handshake(const uint8_t mac_address[6], uint32_t id_device,
                      const struct sockaddr_in* server_addr);

#endif // CONNECTION_H
