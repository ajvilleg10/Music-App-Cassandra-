"""CLI commands implementation using Command pattern.

Adds input validation helpers so each prompt validates and re-asks
until a correct value is provided (cedula/numeric, int/float, email, date...).
"""
from abc import ABC, abstractmethod
from datetime import date
import re
from typing import List, Optional, Set

from ..application.services import MusicService
from ..config.config import load_config


# --- Input validation helpers ---
_config = load_config()
DEFAULT_MAX_RETRIES = _config.max_retries


def prompt_nonempty(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[str]:
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if v:
            return v
        print("Entrada vacía. Intenta de nuevo.")
        tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


def prompt_digits(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[str]:
    """Solicita solo dígitos (números enteros representados como string)."""
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if v.isdigit():
            return v
        print("Por favor ingresa solo números (sin espacios ni signos).")
        tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


def prompt_int(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[int]:
    """Solicita un entero obligatorio (no puede estar vacío)."""
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if not v:
            print("Entrada vacía. Intenta de nuevo.")
            tries += 1
            continue
        if v.lstrip("+-").isdigit():
            try:
                return int(v)
            except ValueError:
                pass
        print("Valor inválido. Ingresa un número entero válido.")
        tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


def prompt_float(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[float]:
    """Solicita un decimal obligatorio (no puede estar vacío)."""
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if not v:
            print("Entrada vacía. Intenta de nuevo.")
            tries += 1
            continue
        try:
            return float(v)
        except ValueError:
            print("Valor inválido. Ingresa un número (decimal) válido.")
            tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def prompt_email(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[str]:
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if EMAIL_RE.match(v):
            return v
        print("Email inválido. Ingresa un email válido (ej: usuario@dominio.com).")
        tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


def prompt_date(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[date]:
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        try:
            y, m, d = map(int, v.split("-"))
            return date(y, m, d)
        except Exception:
            print("Fecha inválida. Usa el formato YYYY-MM-DD y valores válidos.")
            tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


CANCELLED = object()


def prompt_optional_int(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES):
    """Retorna int, None (si el usuario dejó vacío) o CANCELLED (si se agotaron reintentos)."""
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if v == "":
            return None
        if v.lstrip("+-").isdigit():
            return int(v)
        print("Valor inválido. Ingresa un número entero o deja vacío.")
        tries += 1
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return CANCELLED


def prompt_genres(prompt: str, max_retries: int = DEFAULT_MAX_RETRIES) -> Optional[Set[str]]:
    """Solicita géneros separados por coma (obligatorio, no puede estar vacío)."""
    tries = 0
    while tries < max_retries:
        v = input(prompt).strip()
        if not v:
            print("Géneros no pueden estar vacíos. Intenta de nuevo.")
            tries += 1
            continue
        return {g.strip() for g in v.split(",") if g.strip()}
    print("Máximo de intentos alcanzado. Operación cancelada.")
    return None


def check_input(value, field_name: str = "campo") -> bool:
    """Check if input was successful. If None, print error and return False."""
    if value is None:
        print(f"{field_name} inválido. Operación cancelada.")
        return False
    return True


# --- end helpers ---


class Command(ABC):
    """Base command interface."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass


class CrearUsuarioCommand(Command):
    """Command for creating a usuario."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        dni = prompt_digits("DNI (solo números): ")
        if not check_input(dni, "DNI"):
            return
        nombre = prompt_nonempty("Nombre: ")
        if not check_input(nombre, "Nombre"):
            return
        email = prompt_email("Email: ")
        if not check_input(email, "Email"):
            return
        tel = prompt_digits("Teléfono (solo números): ")
        if not check_input(tel, "Teléfono"):
            return

        self.service.crear_usuario(dni, nombre, email, tel)
        print("Usuario insertado exitosamente.")


class CrearCancionCommand(Command):
    """Command for creating a canción."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        isrc = prompt_nonempty("ISRC: ")
        if not check_input(isrc, "ISRC"):
            return
        titulo = prompt_nonempty("Título: ")
        if not check_input(titulo, "Título"):
            return
        anio = prompt_int("Año (int): ")
        if not check_input(anio, "Año"):
            return
        generos = prompt_genres("Géneros (separados por coma): ")
        if not check_input(generos, "Géneros"):
            return
        artista_cod = prompt_int("Artista_Cod (int): ")
        if not check_input(artista_cod, "Artista_Cod"):
            return
        artista_nombre = prompt_nonempty("Artista_Nombre: ")
        if not check_input(artista_nombre, "Artista_Nombre"):
            return
        genero_p = prompt_nonempty("Género principal para partición: ")
        if not check_input(genero_p, "Género principal"):
            return

        self.service.crear_cancion(
            isrc, titulo, anio, generos,
            artista_cod, artista_nombre, genero_p
        )
        print("Canción insertada exitosamente.")


class RegistrarGrabacionCommand(Command):
    """Command for registering a grabación."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        grab_cod = prompt_int("Grabacion_Cod (int): ")
        if not check_input(grab_cod, "Grabacion_Cod"):
            return
        dni = prompt_digits("Usuario_DNI (solo números): ")
        if not check_input(dni, "Usuario_DNI"):
            return
        nombre = prompt_nonempty("Usuario_Nombre: ")
        if not check_input(nombre, "Usuario_Nombre"):
            return
        fecha = prompt_date("Fecha (YYYY-MM-DD): ")
        if not check_input(fecha, "Fecha"):
            return
        duracion = prompt_int("Duración en segundos (int): ")
        if not check_input(duracion, "Duración"):
            return

        self.service.registrar_grabacion(
            grab_cod, dni, nombre, fecha, duracion)
        print("Relación es_guardada_por registrada exitosamente.")


class RegistrarArtistaPaisCommand(Command):
    """Command for registering artist and country relationship."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        isrc = prompt_nonempty("ISRC canción: ")
        if not check_input(isrc, "ISRC"):
            return
        artista_cod = prompt_int("Artista_Cod (int): ")
        if not check_input(artista_cod, "Artista_Cod"):
            return
        artista_nombre = prompt_nonempty("Artista_Nombre: ")
        if not check_input(artista_nombre, "Artista_Nombre"):
            return
        pais_cod = prompt_int("Pais_Cod (int): ")
        if not check_input(pais_cod, "Pais_Cod"):
            return
        pais_nombre = prompt_nonempty("Pais_Nombre: ")
        if not check_input(pais_nombre, "Pais_Nombre"):
            return
        sello_cod = prompt_optional_int("Sello_Cod (int o vacío): ")
        if sello_cod is CANCELLED:
            print("✗ Sello_Cod inválido. Operación cancelada.")
            return
        # sello_cod can be None (user left empty) or an int
        sello_nombre = prompt_nonempty("Sello_Nombre: ")
        if not check_input(sello_nombre, "Sello_Nombre"):
            return
        # Premios es opcional: permite vacío sin re-prompt
        premios_in = input("Premios (separados por coma, o vacío): ").strip()
        premios = {p.strip() for p in premios_in.split(
            ",") if p.strip()} if premios_in else None

        self.service.registrar_artista_pais(
            isrc, artista_cod, artista_nombre,
            pais_cod, pais_nombre, sello_cod, sello_nombre, premios
        )
        print("Relaciones interpretada_por/es_de registradas exitosamente.")


class ActualizarNombreUsuarioCommand(Command):
    """Command for updating usuario name."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        dni = prompt_digits("DNI actual (solo números): ")
        if not check_input(dni, "DNI"):
            return
        nuevo = prompt_nonempty("Nuevo nombre: ")
        if not check_input(nuevo, "Nuevo nombre"):
            return

        self.service.actualizar_nombre_usuario(dni, nuevo)
        print("Nombre actualizado exitosamente.")


class BorrarGrabacionesFechaCommand(Command):
    """Command for deleting grabaciones by date."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        fecha = prompt_date("Fecha (YYYY-MM-DD): ")
        if not check_input(fecha, "Fecha"):
            return

        self.service.borrar_grabaciones_fecha(fecha)
        print("Grabaciones borradas exitosamente.")


class ConsultarUsuariosNombreCommand(Command):
    """Command for querying usuarios by name."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        nombre = prompt_nonempty("Nombre: ")
        if not check_input(nombre, "Nombre"):
            return
        resultados = self.service.buscar_usuarios_por_nombre(nombre)
        if resultados:
            for r in resultados:
                print(r)
        else:
            print("No se encontraron usuarios con ese nombre.")


class ConsultarUsuariosGrabacionCommand(Command):
    """Command for querying usuarios by grabación."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        grab_cod = prompt_int("Grabacion_Cod (int): ")
        if not check_input(grab_cod, "Grabacion_Cod"):
            return
        resultados = self.service.buscar_usuarios_por_grabacion(grab_cod)
        if resultados:
            for r in resultados:
                print(r)
        else:
            print("No se encontraron usuarios para esa grabación.")


class ConsultarArtistaPaisCommand(Command):
    """Command for querying artist and country by ISRC."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        isrc = prompt_nonempty("ISRC: ")
        if not check_input(isrc, "ISRC"):
            return
        resultados = self.service.buscar_artista_pais_por_isrc(isrc)
        if resultados:
            for r in resultados:
                print(r)
        else:
            print("No se encontró información para ese ISRC.")


class ConsultarConteoArtistasPaisCommand(Command):
    """Command for querying artist count by country."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        pais_cod = prompt_int("Pais_Cod (int): ")
        if not check_input(pais_cod, "Pais_Cod"):
            return
        count = self.service.obtener_conteo_artistas_pais(pais_cod)
        print(f"Cantidad de artistas: {count}")


class ConsultarCancionesGeneroCommand(Command):
    """Command for querying canciones by genre."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        genero = prompt_nonempty("Género: ")
        if not check_input(genero, "Género"):
            return
        resultados = self.service.buscar_canciones_por_genero(genero)
        if resultados:
            for r in resultados:
                print(r)
        else:
            print("No se encontraron canciones para ese género.")


class ConsultarGrabacionesFechaCommand(Command):
    """Command for querying grabaciones by date."""

    def __init__(self, service: MusicService):
        self.service = service

    def execute(self) -> None:
        fecha = prompt_date("Fecha (YYYY-MM-DD): ")
        if not check_input(fecha, "Fecha"):
            return
        resultados = self.service.buscar_grabaciones_por_fecha(
            date(fecha.year, fecha.month, fecha.day))
        if resultados:
            for r in resultados:
                print(r)
        else:
            print("No se encontraron grabaciones para esa fecha.")
