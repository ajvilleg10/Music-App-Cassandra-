"""Repository interfaces for the music application."""
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from ..domain.models import Usuario, Cancion, Grabacion, Artista

class IUsuarioRepository(ABC):
    """Interface for Usuario repository."""
    
    @abstractmethod
    def get_by_dni(self, dni: str) -> List[Usuario]:
        """Get usuario by DNI."""
        pass
    
    @abstractmethod
    def get_by_nombre(self, nombre: str) -> List[Usuario]:
        """Get usuario by nombre."""
        pass
    
    @abstractmethod
    def save(self, usuario: Usuario) -> None:
        """Save usuario."""
        pass
    
    @abstractmethod
    def update_nombre(self, dni: str, nuevo_nombre: str) -> None:
        """Update usuario nombre."""
        pass

class ICancionRepository(ABC):
    """Interface for Cancion repository."""
    
    @abstractmethod
    def get_by_isrc(self, isrc: str, genero_hint: Optional[str] = None) -> List[Cancion]:
        """Get cancion by ISRC."""
        pass
    
    @abstractmethod
    def get_by_genero(self, genero: str) -> List[Cancion]:
        """Get canciones by género."""
        pass
    
    @abstractmethod
    def save(self, cancion: Cancion) -> None:
        """Save cancion."""
        pass

class IGrabacionRepository(ABC):
    """Interface for Grabacion repository."""
    
    @abstractmethod
    def get_by_codigo(self, codigo: int) -> List[Grabacion]:
        """Get grabacion by código."""
        pass
    
    @abstractmethod
    def get_by_fecha(self, fecha: date) -> List[Grabacion]:
        """Get grabaciones by fecha."""
        pass
    
    @abstractmethod
    def save(self, grabacion: Grabacion) -> None:
        """Save grabacion."""
        pass
    
    @abstractmethod
    def delete_by_fecha(self, fecha: date) -> None:
        """Delete grabaciones by fecha."""
        pass

class IArtistaRepository(ABC):
    """Interface for Artista repository."""
    
    @abstractmethod
    def save_with_pais(self, artista: Artista) -> None:
        """Save artista with país information."""
        pass
    
    @abstractmethod
    def get_count_by_pais(self, pais_cod: int) -> int:
        """Get artist count by país."""
        pass