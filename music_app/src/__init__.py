"""Music application package."""
from .config.config import AppConfig, load_config
from .domain.models import Usuario, Cancion, Grabacion, Artista
from .application.services import MusicService

__version__ = "1.0.0"
__all__ = [
    "AppConfig",
    "load_config",
    "Usuario",
    "Cancion",
    "Grabacion",
    "Artista",
    "MusicService"
]