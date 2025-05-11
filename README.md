## Tarea 1 de IoT

### Integrantes

- Joaquin Cornejo
- Oscar Garrido
- Lucas Llort


### Preambulo

Primero es necesario crear un `.env`, se puede tomar el archivo `example.env` como base, el cual ya tiene las variables necesarias definidas, también es necesario poner la interfaz de red de la raspberry en modo AP, la forma más simple de hacer esto es con el siguiente comando:
```bash
sudo nmcli device wifi hotspot con-name hotspot ifname wlan0 ssid <ssid> password <contraseña>
```
Para saber el nombre de las interfaces de red disponibles de red se puede usar el comando `ip link`, es importante saber que activar el hotspot la interfaz de red debe cambiar de modo cliente a modo AP, por lo que la conección al internet se verá cortada, eso incluye la conección por ssh, por lo que se deberá conectar el computador directo a la red de la Raspberry Pi para restablecer la conección.

Dependiendo de la configuración que tenga la Raspberry Pi previamente, puede que sea necesario abrir un puerto en la firewall para que el servidor pueda recibir conecciónes externas, esto se puede hacer con los siguientes comandos:
```bash
sudo iptables -I INPUT -p tcp --dport <puerto del server> -j ACCEPT
sudo iptables -I INPUT -p udp --dport <puerto del server> -j ACCEPT
```

Finalmente, es necesario configurar las credenciales de la red Wi-Fi para el ESP, esto se debe hacer con el comando `idf.py menuconfig`, navegando a la sección "Project Configuration".


### Ejecución del servidor

Se utilizó docker para hostear tanto la base de datos como para el servidor, por lo que ambos servicios se pueden iniciar con el siguiente comando:

```bash
docker compose up --build
```

### Ejecución del cliente

Se debe cargar en el ESP igual que cualquier otro proyecto hecho con esp-idf:

```bash
idf.py build flash monitor
```


