"""Main CLI application."""
from .presentation.commands import (
    Command,
    CrearUsuarioCommand,
    CrearCancionCommand,
    RegistrarGrabacionCommand,
    RegistrarArtistaPaisCommand,
    ActualizarNombreUsuarioCommand,
    BorrarGrabacionesFechaCommand,
    ConsultarUsuariosNombreCommand,
    ConsultarUsuariosGrabacionCommand,
    ConsultarArtistaPaisCommand,
    ConsultarConteoArtistasPaisCommand,
    ConsultarCancionesGeneroCommand,
    ConsultarGrabacionesFechaCommand
)
from .infrastructure.init_db import initialize_database, verify_connection
from .infrastructure.repositories import (
    CassandraUsuarioRepository,
    CassandraCancionRepository,
    CassandraGrabacionRepository,
    CassandraArtistaRepository
)
from .application.services import MusicService
from .config.config import load_config, AppConfig
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from cassandra.cluster import Cluster, Session
from typing import Dict, Type

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')


logger = logging.getLogger(__name__)


def setup_logging(config: AppConfig) -> None:
    """Configure logging based on application config."""
    logging.basicConfig(
        level=config.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=config.log_file
    )


def get_cassandra_session(config: AppConfig) -> Session:
    """Get Cassandra session using configuration."""
    try:
        cluster = Cluster(
            contact_points=config.cassandra.contact_points,
            port=config.cassandra.port,
            auth_provider=None  # Add auth if needed
        )
        session = cluster.connect(config.cassandra.keyspace)
        return session
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {e}")
        raise


def setup_repositories(session: Session) -> MusicService:
    """Initialize repositories and service layer."""
    usuario_repo = CassandraUsuarioRepository(session)
    cancion_repo = CassandraCancionRepository(session)
    grabacion_repo = CassandraGrabacionRepository(session)
    artista_repo = CassandraArtistaRepository(session)

    return MusicService(
        usuario_repo=usuario_repo,
        cancion_repo=cancion_repo,
        grabacion_repo=grabacion_repo,
        artista_repo=artista_repo
    )


def get_commands() -> Dict[str, Type[Command]]:
    """Get mapping of command options to command classes."""
    return {
        "1": CrearUsuarioCommand,
        "2": CrearCancionCommand,
        "3": RegistrarGrabacionCommand,
        "4": RegistrarArtistaPaisCommand,
        "5": ActualizarNombreUsuarioCommand,
        "6": BorrarGrabacionesFechaCommand,
        "7": ConsultarUsuariosNombreCommand,
        "8": ConsultarUsuariosGrabacionCommand,
        "9": ConsultarArtistaPaisCommand,
        "10": ConsultarConteoArtistasPaisCommand,
        "11": ConsultarCancionesGeneroCommand,
        "12": ConsultarGrabacionesFechaCommand
    }


def handle_init_db(config: AppConfig) -> None:
    """Initialize database schema."""
    print("Inicializando base de datos...")
    try:
        initialize_database(
            contact_points=config.cassandra.contact_points,
            port=config.cassandra.port,
            username=config.cassandra.username,
            password=config.cassandra.password,
            keyspace=None  # Don't connect to keyspace initially
        )
        print("✓ Base de datos inicializada correctamente")
        logger.info("Database initialization completed")
    except Exception as e:
        print(f"✗ Error al inicializar la base de datos: {e}")
        logger.error(f"Database initialization error: {e}")
        sys.exit(1)


def handle_verify_connection(config: AppConfig) -> None:
    """Verify database connection."""
    print("Verificando conexión a Cassandra...")
    try:
        if verify_connection(
            contact_points=config.cassandra.contact_points,
            port=config.cassandra.port,
            keyspace=config.cassandra.keyspace,
            username=config.cassandra.username,
            password=config.cassandra.password
        ):
            print("✓ Conexión verificada correctamente")
            logger.info("Connection verified")
        else:
            print("✗ Error al conectar")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Connection verification error: {e}")
        sys.exit(1)


def handle_cli_commands() -> bool:
    """Handle command-line arguments. Returns True if a command was executed."""
    if len(sys.argv) <= 1:
        return False

    command = sys.argv[1]
    config = load_config()
    setup_logging(config)

    if command == "--init-db":
        handle_init_db(config)
    elif command == "--verify-connection":
        handle_verify_connection(config)
    elif command == "--help":
        print("""
Uso: python -m src [comando]

Comandos disponibles:
  --init-db              Inicializar base de datos con esquema
  --verify-connection    Verificar conexión a Cassandra
  --help                 Mostrar esta ayuda
  (sin argumentos)       Iniciar aplicación interactiva
        """)
    else:
        print(f"Comando desconocido: {command}")
        sys.exit(1)

    return True


def run_interactive_menu(service: MusicService, commands: Dict[str, Type[Command]]) -> None:
    """Run the interactive menu loop."""
    menu = """
Seleccione una opción:
 1) Insertar Usuario (Tabla1)
 2) Insertar Canción (Tabla5)
 3) Registrar 'es_guardada_por' (Tablas 2 y 6)
 4) Registrar 'es_interpretada_por' y 'es_de' (Tablas 3 y 4)
 5) Actualizar nombre de usuario por DNI (Tabla1)
 6) Borrar grabaciones por fecha (Tabla6)
 7) Consultar usuarios por nombre (Tabla1)
 8) Consultar usuarios por grabación (Tabla2)
 9) Consultar países de artistas por ISRC (Tabla3)
10) Consultar conteo artistas por país (Tabla4)
11) Consultar canciones por género (Tabla5)
12) Consultar grabaciones por fecha (Tabla6)
 0) Salir
> """

    while True:
        try:
            op = input(menu).strip()
        except EOFError:
            break

        if op == "0":
            print("Saliendo...")
            break

        try:
            if op in commands:
                command = commands[op](service)
                command.execute()
            else:
                print("Opción inválida.")
        except ValueError as e:
            logger.error(f"Error de formato en los datos: {e}")
            print(f"Error de formato en los datos: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")


def main() -> None:
    """Main application entry point."""
    if handle_cli_commands():
        return

    # Load configuration
    config = load_config()
    setup_logging(config)

    logger.info("Starting music application...")

    try:
        # Setup infrastructure
        session = get_cassandra_session(config)
        service = setup_repositories(session)
        commands = get_commands()

        # Run interactive menu
        run_interactive_menu(service, commands)

    except Exception as e:
        logger.error(f"Error fatal: {e}")
        print(f"Error fatal: {e}")
    finally:
        logger.info("Cerrando aplicación...")


if __name__ == "__main__":
    main()
