# Music App — Guía mínima de ejecución

Aplicación Python para gestionar músicas, artistas y grabaciones usando Apache Cassandra.

## Resumen rápido (Windows / PowerShell)

```powershell
cd /ruta/al/proyecto/music_app
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker-compose up -d
python -m src --init-db
python -m src
```



## Requisitos

- Python 3.8+
- Docker Desktop en ejecución

## Instalación

1. Navega a la carpeta del proyecto en PowerShell:

```powershell
cd /ruta/al/proyecto/music_app
```

2. Crea un entorno virtual:

```powershell
python -m venv venv
```

3. Activa el entorno virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

4. Instala dependencias:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```



## Configuración (.env)

El proyecto carga `.env` automáticamente desde `src/__main__.py`. El archivo ya está incluido en el repositorio.

Verifica que contiene:

```
CASSANDRA_HOSTS=127.0.0.1
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=alexvillegas
CASSANDRA_USERNAME=
CASSANDRA_PASSWORD=
LOG_LEVEL=INFO
LOG_FILE=app.log
```



## Iniciar Cassandra (Docker)

```powershell
docker-compose up -d
```

Verifica con:

```powershell
docker ps
```

El contenedor puede tardar 30–60 segundos en estar listo.



## Inicializar Base de Datos

```powershell
python -m src --init-db
```

Esto ejecuta `scripts/init_schema.cql` para crear el keyspace `alexvillegas` y todas las tablas.

## Verificar Conexión

```powershell
python -m src --verify-connection
```

## Ejecutar la Aplicación

```powershell
python -m src
```

Sigue el menú interactivo para registrar artistas, canciones y grabaciones.



## Comandos útiles

```powershell
# Levantar Docker
docker-compose up -d

# Detener Docker
docker-compose down

# Inicializar BD
python -m src --init-db

# Ver conexión
python -m src --verify-connection

# Ver logs del contenedor
docker logs -f music_app_cassandra
```

## Solución rápida de problemas

- **Si la app no conecta:** asegúrate de que Docker está corriendo y el contenedor Cassandra está arriba.
- **Si `python -m src --init-db` falla:** revisa `scripts/init_schema.cql` y los logs del contenedor con `docker logs music_app_cassandra`.

## Estructura mínima del proyecto

```
music_app/
├── src/
│   ├── __main__.py              # Entrada, carga .env, menú CLI
│   ├── application/
│   │   └── services.py          # Lógica de negocio
│   ├── config/
│   │   └── config.py            # Lectura de .env
│   ├── domain/
│   │   ├── models.py            # Modelos (Artista, Grabacion, etc.)
│   │   └── repositories.py      # Interfaces de repositorios
│   ├── infrastructure/
│   │   ├── repositories.py      # Implementación Cassandra
│   │   ├── cassandra_client.py  # Cliente Cassandra
│   │   └── init_db.py           # Inicialización BD
│   └── presentation/
│       └── commands.py          # Comandos CLI
├── scripts/
│   └── init_schema.cql          # Schema Cassandra
├── docker-compose.yml           # Configuración Docker
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno (local)
└── README.md                    # Este archivo
```

## Notas de diseño

- El proyecto usa separación por capas (presentation, application, domain, infrastructure).
- Se agregó persistencia para: `Grabacion.duracion:int` y `Artista.premios:set<text>`.
- El cliente Cassandra maneja reintentos y reconexión automática.

---

Autor: Alex Villegas
