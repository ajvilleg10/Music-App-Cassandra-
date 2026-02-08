"""Database initialization utilities."""
import logging
import os
from pathlib import Path
from .cassandra_client import CassandraClient

logger = logging.getLogger(__name__)


def get_schema_path() -> str:
    """Get path to schema.cql file."""
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "scripts" / "init_schema.cql",
        Path("scripts") / "init_schema.cql",
        Path.cwd() / "scripts" / "init_schema.cql",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    raise FileNotFoundError(
        f"init_schema.cql not found. Searched in: {[str(p) for p in possible_paths]}"
    )


def initialize_database(
    contact_points: list,
    port: int = 9042,
    username: str = None,
    password: str = None,
    keyspace: str = None
) -> None:
    """
    Initialize Cassandra database with schema.

    Args:
        contact_points: List of Cassandra contact points
        port: Cassandra port
        username: Optional authentication username
        password: Optional authentication password
        keyspace: Optional keyspace to connect to (for initial connection)
    """
    client = CassandraClient(
        contact_points=contact_points,
        port=port,
        keyspace=keyspace,
        username=username,
        password=password
    )

    try:
        # Connect to system keyspace to create new keyspace
        logger.info("Connecting to Cassandra for schema initialization...")
        client.connect(use_system_keyspace=True)

        # Execute schema file
        schema_path = get_schema_path()
        logger.info(f"Executing schema from: {schema_path}")
        client.execute_cql_file(schema_path)

        logger.info("✓ Database initialization completed successfully")

    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        raise
    finally:
        client.shutdown()


def verify_connection(
    contact_points: list,
    port: int = 9042,
    keyspace: str = None,
    username: str = None,
    password: str = None
) -> bool:
    """
    Verify connection to Cassandra.

    Args:
        contact_points: List of Cassandra contact points
        port: Cassandra port
        keyspace: Keyspace to connect to
        username: Optional authentication username
        password: Optional authentication password

    Returns:
        True if connection successful, False otherwise
    """
    client = CassandraClient(
        contact_points=contact_points,
        port=port,
        keyspace=keyspace,
        username=username,
        password=password
    )

    try:
        logger.info("Verifying connection to Cassandra...")
        client.connect(use_system_keyspace=True)
        result = client.session.execute("SELECT now() FROM system.local;")
        timestamp = result[0][0] if result else "unknown"
        logger.info(f"✓ Connection verified. Server time: {timestamp}")
        return True
    except Exception as e:
        logger.error(f"✗ Connection verification failed: {str(e)}")
        return False
    finally:
        client.shutdown()
