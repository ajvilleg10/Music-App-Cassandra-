"""Cassandra repository implementations."""
from datetime import date
from typing import List, Optional
from cassandra.cluster import Session
from cassandra.query import SimpleStatement

from ..domain.models import Usuario, Cancion, Grabacion, Artista
from ..domain.repositories import (
    IUsuarioRepository,
    ICancionRepository,
    IGrabacionRepository,
    IArtistaRepository
)


class CassandraUsuarioRepository(IUsuarioRepository):
    """Cassandra implementation of IUsuarioRepository."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_dni(self, dni: str) -> List[Usuario]:
        query = SimpleStatement(
            "SELECT * FROM USERS_BY_NAME WHERE Usuario_DNI = %s ALLOW FILTERING",
            fetch_size=100
        )
        rows = self.session.execute(query, [dni])
        return [
            Usuario(
                nombre=row.usuario_nombre,
                dni=row.usuario_dni,
                email=row.usuario_email,
                telefono=row.usuario_telefono
            )
            for row in rows
        ]

    def get_by_nombre(self, nombre: str) -> List[Usuario]:
        query = SimpleStatement(
            "SELECT * FROM USERS_BY_NAME WHERE Usuario_Nombre = %s"
        )
        rows = self.session.execute(query, [nombre])
        return [
            Usuario(
                nombre=row.usuario_nombre,
                dni=row.usuario_dni,
                email=row.usuario_email,
                telefono=row.usuario_telefono
            )
            for row in rows
        ]

    def save(self, usuario: Usuario) -> None:
        query = SimpleStatement("""
            INSERT INTO USERS_BY_NAME (
                Usuario_Nombre,
                Usuario_DNI,
                Usuario_Email,
                Usuario_Telefono
            )
            VALUES (%s, %s, %s, %s)
        """)
        self.session.execute(query, [
            usuario.nombre,
            usuario.dni,
            usuario.email,
            usuario.telefono
        ])

    def update_nombre(self, dni: str, nuevo_nombre: str) -> None:
        # Get current user data
        usuarios = self.get_by_dni(dni)
        for usuario in usuarios:
            # Guardar nombre antiguo ANTES de actualizar
            nombre_antiguo = usuario.nombre

            # Borrar registro antiguo primero (con el nombre antiguo)
            query_delete = SimpleStatement(
                "DELETE FROM USERS_BY_NAME WHERE Usuario_Nombre = %s AND Usuario_DNI = %s"
            )
            self.session.execute(query_delete, [nombre_antiguo, usuario.dni])

            # Actualizar nombre y guardar nuevo registro
            usuario.nombre = nuevo_nombre
            self.save(usuario)


class CassandraCancionRepository(ICancionRepository):
    """Cassandra implementation of ICancionRepository."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_isrc(self, isrc: str, genero_hint: Optional[str] = None) -> List[Cancion]:
        if genero_hint:
            query = SimpleStatement(
                "SELECT * FROM MUSICS_BY_GENDER WHERE Cancion_Genero = %s AND Cancion_ISRC = %s"
            )
            rows = self.session.execute(query, [genero_hint, isrc])
        else:
            query = SimpleStatement(
                "SELECT * FROM MUSICS_BY_GENDER WHERE Cancion_ISRC = %s"
            )
            rows = self.session.execute(query, [isrc])

        return [
            Cancion(
                isrc=row.cancion_isrc,
                titulo=row.cancion_titulo,
                anio=row.cancion_anio,
                generos=row.cancion_generos,
                genero_principal=row.cancion_genero,
                artista_cod=row.artista_cod,
                artista_nombre=row.artista_nombre
            )
            for row in rows
        ]

    def get_by_genero(self, genero: str) -> List[Cancion]:
        query = SimpleStatement(
            "SELECT * FROM MUSICS_BY_GENDER WHERE Cancion_Genero = %s"
        )
        rows = self.session.execute(query, [genero])
        return [
            Cancion(
                isrc=row.cancion_isrc,
                titulo=row.cancion_titulo,
                anio=row.cancion_anio,
                generos=row.cancion_generos,
                genero_principal=row.cancion_genero,
                artista_cod=row.artista_cod,
                artista_nombre=row.artista_nombre
            )
            for row in rows
        ]

    def save(self, cancion: Cancion) -> None:
        query = SimpleStatement("""
            INSERT INTO MUSICS_BY_GENDER (
                Cancion_Genero,
                Cancion_ISRC,
                Cancion_Titulo,
                Cancion_Anio,
                Cancion_Generos,
                Artista_Cod,
                Artista_Nombre
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """)
        self.session.execute(query, [
            cancion.genero_principal,
            cancion.isrc,
            cancion.titulo,
            cancion.anio,
            cancion.generos,
            cancion.artista_cod,
            cancion.artista_nombre
        ])


class CassandraGrabacionRepository(IGrabacionRepository):
    """Cassandra implementation of IGrabacionRepository."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_codigo(self, codigo: int) -> List[Grabacion]:
        # Obtener usuarios asociados a la grabación desde Tabla2 (ahora incluye la fecha)
        query = SimpleStatement(
            "SELECT * FROM USERS_BY_RECORD WHERE Grabacion_Cod = %s"
        )
        rows = self.session.execute(query, [codigo])
        return [
            Grabacion(
                codigo=row.grabacion_cod,
                usuario_dni=row.usuario_dni,
                usuario_nombre=row.usuario_nombre,
                fecha_guardado=row.esguardadapor_fecha if hasattr(
                    row, 'esguardadapor_fecha') else None,
                duracion=row.duracion if hasattr(row, 'duracion') else None
            )
            for row in rows
        ]

    def get_by_fecha(self, fecha: date) -> List[Grabacion]:
        query = SimpleStatement(
            "SELECT * FROM RECORDS_BY_DATE WHERE EsGuardadaPor_Fecha = %s"
        )
        rows = self.session.execute(query, [fecha])
        return [
            Grabacion(
                codigo=row.grabacion_cod,
                usuario_dni=row.usuario_dni,
                usuario_nombre=row.usuario_nombre,
                fecha_guardado=row.esguardadapor_fecha,
                duracion=row.duracion if hasattr(row, 'duracion') else None
            )
            for row in rows
        ]

    def save(self, grabacion: Grabacion) -> None:
        # Insert into Tabla2 (ahora con fecha)
        query2 = SimpleStatement("""
            INSERT INTO USERS_BY_RECORD (
                Grabacion_Cod,
                Usuario_DNI,
                Usuario_Nombre,
                Usuario_Email,
                Usuario_Telefono,
                EsGuardadaPor_Fecha,
                Duracion
            )
            VALUES (%s, %s, %s, NULL, NULL, %s, %s)
        """)
        self.session.execute(query2, [
            grabacion.codigo,
            grabacion.usuario_dni,
            grabacion.usuario_nombre,
            grabacion.fecha_guardado,
            grabacion.duracion
        ])

        # Insert into Tabla6
        query6 = SimpleStatement("""
            INSERT INTO RECORDS_BY_DATE (
                EsGuardadaPor_Fecha,
                Grabacion_Cod,
                Usuario_DNI,
                Usuario_Nombre,
                Duracion
            )
            VALUES (%s, %s, %s, %s, %s)
        """)
        self.session.execute(query6, [
            grabacion.fecha_guardado,
            grabacion.codigo,
            grabacion.usuario_dni,
            grabacion.usuario_nombre,
            grabacion.duracion
        ])

    def delete_by_fecha(self, fecha: date) -> None:
        # First get all grabaciones for the date
        grabaciones = self.get_by_fecha(fecha)

        # Delete each grabacion
        query = SimpleStatement("""
            DELETE FROM RECORDS_BY_DATE
            WHERE EsGuardadaPor_Fecha = %s 
            AND Grabacion_Cod = %s 
            AND Usuario_DNI = %s
        """)
        for grabacion in grabaciones:
            self.session.execute(query, [
                fecha,
                grabacion.codigo,
                grabacion.usuario_dni
            ])


class CassandraArtistaRepository(IArtistaRepository):
    """Cassandra implementation of IArtistaRepository."""

    def __init__(self, session: Session):
        self.session = session

    def save_with_pais(self, artista: Artista) -> None:
        # Insert into Tabla3
        query3 = SimpleStatement("""
            INSERT INTO MAPPING_ISRC (
                Cancion_ISRC,
                Pais_Cod,
                Artista_Cod,
                Pais_Nombre,
                Artista_Nombre,
                Sello_Cod,
                Sello_Nombre,
                Premios
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """)
        self.session.execute(query3, [
            artista.isrc if hasattr(artista, 'isrc') else None,
            artista.pais_cod,
            artista.codigo,
            artista.pais_nombre,
            artista.nombre,
            artista.sello_cod,
            artista.sello_nombre,
            artista.premios if hasattr(artista, 'premios') else set()
        ])

        # Update counter in Tabla4
        query4 = SimpleStatement("""
            UPDATE ARTISTS_BY_COUNTRY
            SET Artista_Count = Artista_Count + 1 
            WHERE Pais_Cod = %s
        """)
        self.session.execute(query4, [artista.pais_cod])

    def get_count_by_pais(self, pais_cod: int) -> int:
        query = SimpleStatement(
            "SELECT Artista_Count FROM ARTISTS_BY_COUNTRY WHERE Pais_Cod = %s"
        )
        rows = list(self.session.execute(query, [pais_cod]))
        return rows[0].artista_count if rows else 0
