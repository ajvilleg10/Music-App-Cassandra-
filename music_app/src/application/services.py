"""Service layer for business logic."""
from datetime import date
from typing import List, Optional, Set
from cassandra.query import SimpleStatement

from ..domain.models import Usuario, Cancion, Grabacion, Artista
from ..domain.repositories import (
    IUsuarioRepository,
    ICancionRepository,
    IGrabacionRepository,
    IArtistaRepository
)


class MusicService:
    """Service layer implementing business logic."""

    def __init__(
        self,
        usuario_repo: IUsuarioRepository,
        cancion_repo: ICancionRepository,
        grabacion_repo: IGrabacionRepository,
        artista_repo: IArtistaRepository
    ):
        self.usuario_repo = usuario_repo
        self.cancion_repo = cancion_repo
        self.grabacion_repo = grabacion_repo
        self.artista_repo = artista_repo

    def crear_usuario(
        self,
        dni: str,
        nombre: str,
        email: str,
        telefono: str
    ) -> None:
        """Create a new usuario."""
        usuario = Usuario(
            nombre=nombre,
            dni=dni,
            email=email,
            telefono=telefono
        )
        self.usuario_repo.save(usuario)

    def crear_cancion(
        self,
        isrc: str,
        titulo: str,
        anio: int,
        generos: Set[str],
        artista_cod: int,
        artista_nombre: str,
        genero_principal: str
    ) -> None:
        """Create a new canción."""
        cancion = Cancion(
            isrc=isrc,
            titulo=titulo,
            anio=anio,
            generos=generos,
            artista_cod=artista_cod,
            artista_nombre=artista_nombre,
            genero_principal=genero_principal
        )
        self.cancion_repo.save(cancion)

    def registrar_grabacion(
        self,
        grabacion_cod: int,
        usuario_dni: str,
        usuario_nombre: str,
        fecha: date,
        duracion: int = 0
    ) -> None:
        """Register a new grabación."""
        grabacion = Grabacion(
            codigo=grabacion_cod,
            usuario_dni=usuario_dni,
            usuario_nombre=usuario_nombre,
            fecha_guardado=fecha,
            duracion=duracion
        )
        self.grabacion_repo.save(grabacion)

    def registrar_artista_pais(
        self,
        cancion_isrc: str,
        artista_cod: int,
        artista_nombre: str,
        pais_cod: int,
        pais_nombre: str,
        sello_cod: Optional[int] = None,
        sello_nombre: Optional[str] = None,
        premios: Optional[Set[str]] = None
    ) -> None:
        """Register artist and country relationship."""
        artista = Artista(
            codigo=artista_cod,
            nombre=artista_nombre,
            pais_cod=pais_cod,
            pais_nombre=pais_nombre,
            sello_cod=sello_cod,
            sello_nombre=sello_nombre,
            premios=premios if premios is not None else set()
        )
        setattr(artista, 'isrc', cancion_isrc)  # Add ISRC for mapping
        self.artista_repo.save_with_pais(artista)

    def actualizar_nombre_usuario(
        self,
        dni: str,
        nuevo_nombre: str
    ) -> None:
        """Update usuario name."""
        self.usuario_repo.update_nombre(dni, nuevo_nombre)

    def borrar_grabaciones_fecha(
        self,
        fecha: date
    ) -> None:
        """Delete grabaciones by date."""
        self.grabacion_repo.delete_by_fecha(fecha)

    # Query methods
    def buscar_usuarios_por_nombre(
        self,
        nombre: str
    ) -> List[Usuario]:
        """Search usuarios by name."""
        return self.usuario_repo.get_by_nombre(nombre)

    def buscar_usuarios_por_grabacion(
        self,
        grabacion_cod: int
    ) -> List[Grabacion]:
        """Search usuarios by grabación code."""
        return self.grabacion_repo.get_by_codigo(grabacion_cod)

    def buscar_artista_pais_por_isrc(
        self,
        isrc: str
    ) -> List[Artista]:
        """
        Search artist and country by ISRC.

        Este método obtiene información combinada de Tabla5 (canciones) 
        y Tabla3 (relación artista-país).
        """
        # Primero buscamos en Tabla3 que tiene la información completa
        query = SimpleStatement(
            "SELECT * FROM MAPPING_ISRC WHERE Cancion_ISRC = %s")
        rows = self.artista_repo.session.execute(query, [isrc])
        artistas_tabla3 = [
            Artista(
                codigo=row.artista_cod,
                nombre=row.artista_nombre,
                pais_cod=row.pais_cod,
                pais_nombre=row.pais_nombre,
                sello_cod=row.sello_cod,
                sello_nombre=row.sello_nombre,
                premios=set(row.premios) if hasattr(
                    row, 'premios') and row.premios is not None else set()
            )
            for row in rows
        ]

        # Si encontramos resultados en Tabla3, los devolvemos
        if artistas_tabla3:
            return artistas_tabla3

        # Si no hay resultados en Tabla3, buscamos en Tabla5
        canciones = self.cancion_repo.get_by_isrc(isrc)
        return [
            Artista(
                codigo=c.artista_cod,
                nombre=c.artista_nombre,
                pais_cod=None,  # No disponible en Tabla5
                pais_nombre=None  # No disponible en Tabla5
            )
            for c in canciones
        ]

    def obtener_conteo_artistas_pais(
        self,
        pais_cod: int
    ) -> int:
        """Get artist count by country."""
        return self.artista_repo.get_count_by_pais(pais_cod)

    def buscar_canciones_por_genero(
        self,
        genero: str
    ) -> List[Cancion]:
        """Search canciones by genre."""
        return self.cancion_repo.get_by_genero(genero)

    def buscar_grabaciones_por_fecha(
        self,
        fecha: date
    ) -> List[Grabacion]:
        """Search grabaciones by date."""
        return self.grabacion_repo.get_by_fecha(fecha)
