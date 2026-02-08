-- Crear keyspace si no existe
CREATE KEYSPACE IF NOT EXISTS alexvillegas WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Tabla1: Usuarios por nombre
CREATE TABLE IF NOT EXISTS alexvillegas.USERS_BY_NAME (
    Usuario_Nombre text,
    Usuario_DNI text,
    Usuario_Email text,
    Usuario_Telefono text,
    PRIMARY KEY (Usuario_Nombre, Usuario_DNI)
);

-- Índice secundario para búsqueda por DNI
CREATE INDEX IF NOT EXISTS idx_users_by_name_usuario_dni ON alexvillegas.USERS_BY_NAME (Usuario_DNI);

-- Tabla2: Usuarios por grabación
CREATE TABLE IF NOT EXISTS alexvillegas.USERS_BY_RECORD (
    Grabacion_Cod int,
    Usuario_DNI text,
    Usuario_Nombre text,
    Usuario_Email text,
    Usuario_Telefono text,
    EsGuardadaPor_Fecha date,
    Duracion int,
    PRIMARY KEY (Grabacion_Cod, Usuario_DNI)
);

-- Tabla3: Mapeo ISRC -> (País, Artista)
CREATE TABLE IF NOT EXISTS alexvillegas.MAPPING_ISRC (
    Cancion_ISRC text,
    Pais_Cod int,
    Artista_Cod int,
    Pais_Nombre text,
    Artista_Nombre text,
    Sello_Cod int,
    Sello_Nombre text,
    Premios set<text>,
    PRIMARY KEY (Cancion_ISRC)
);

-- Tabla4: Contador de artistas por país
CREATE TABLE IF NOT EXISTS alexvillegas.ARTISTS_BY_COUNTRY (
    Pais_Cod int PRIMARY KEY,
    Artista_Count counter
);

-- Tabla5: Canciones por género
CREATE TABLE IF NOT EXISTS alexvillegas.MUSICS_BY_GENDER (
    Cancion_Genero text,
    Cancion_ISRC text,
    Cancion_Titulo text,
    Cancion_Anio int,
    Cancion_Generos set<text>,
    Artista_Cod int,
    Artista_Nombre text,
    PRIMARY KEY (Cancion_Genero, Cancion_ISRC)
);

-- Índice secundario para búsqueda por ISRC
CREATE INDEX IF NOT EXISTS idx_music_by_gender_music_isrc ON alexvillegas.MUSICS_BY_GENDER (Cancion_ISRC);

-- Tabla6: Grabaciones por fecha
CREATE TABLE IF NOT EXISTS alexvillegas.RECORDS_BY_DATE (
    EsGuardadaPor_Fecha date,
    Grabacion_Cod int,
    Usuario_DNI text,
    Usuario_Nombre text,
    Duracion int,
    PRIMARY KEY (EsGuardadaPor_Fecha, Grabacion_Cod, Usuario_DNI)
);
