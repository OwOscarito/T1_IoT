#ifndef WIFI_H
#define WIFI_H

// Credenciales de la red Wifi (configurar con idf.py menuconfig)
#define WIFI_SSID CONFIG_WIFI_SSID
#define WIFI_PASSWORD CONFIG_WIFI_PASSWORD
#define SERVER_IP CONFIG_SERVER_IP
#define SERVER_PORT CONFIG_SERVER_PORT

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1

void wifi_init_sta(char* ssid, char* password);

#endif // WIFI_H
