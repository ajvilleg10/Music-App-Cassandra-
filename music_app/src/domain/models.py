"""Domain models for the music application."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Set


@dataclass
class Usuario:
    """Usuario entity."""
    nombre: str
    dni: str
    email: str
    telefono: str


@dataclass
class Cancion:
    """Canción entity."""
    isrc: str
    titulo: str
    anio: int
    generos: Set[str]
    genero_principal: str
    artista_cod: int
    artista_nombre: str


@dataclass
class Grabacion:
    """Grabación entity."""
    codigo: int
    usuario_dni: str
    usuario_nombre: str
    fecha_guardado: date
    duracion: int


@dataclass
class Artista:
    """Artista entity."""
    codigo: int
    nombre: str
    pais_cod: int
    pais_nombre: str
    sello_cod: Optional[int] = None
    sello_nombre: Optional[str] = None
    premios: Set[str] = field(default_factory=set)
