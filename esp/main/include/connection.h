#ifndef CONNECTION_H
#define CONNECTION_H

#include <stdint.h>
#include <socket.h>

enum TransportLayer{
    TCP = 0,
    UDP = 1
};

typedef struct {
    enum TransportLayer transport_layer;
    uint8_t id_protocol;
} db_config_t;

int gen_tcp_socket();
int gen_udp_socket();

ssize_t send_data(int sock, void *data, ssize_t data_len);
ssize_t receive_data(int sock, void *buf, ssize_t buf_len);

int query_config(db_config_t *db_conf);

#endif // CONNECTION_H
