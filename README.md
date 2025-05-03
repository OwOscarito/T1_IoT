## T1_IoT

### Integrantes

- Joaquin Cornejo
- Oscar Garrido
- Lucas Llort


_Aqui deben de hacer un readme con la estrucutra y flujo basico de su arquitectura_

## Comandos de docker


### Iniciar la base de datos

```bash
docker compose up -d
```

### Detener la base de datos

```bash
docker compose down
```

### Conectarse a la base de datos con psql

```bash
sudo docker exec -it <nombre contenedor> psql -U <usuario postgres> -d <base de datos> -W
```

### Borrar la base de datos

```bash
docker volume rm postgres_data_iot
```
