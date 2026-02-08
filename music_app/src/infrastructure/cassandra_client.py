"""Cassandra client module for database initialization and connection management."""
import logging
import time
from typing import Optional
from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import FallthroughRetryPolicy

logger = logging.getLogger(__name__)


class CassandraClient:
    """Manages Cassandra cluster and session connections."""

    def __init__(
        self,
        contact_points: list,
        port: int = 9042,
        keyspace: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        max_retries: int = 5,
        retry_delay: int = 2
    ):
        """
        Initialize Cassandra client.

        Args:
            contact_points: List of Cassandra node IPs/hostnames
            port: Cassandra port (default 9042)
            keyspace: Default keyspace to connect to
            username: Optional username for authentication
            password: Optional password for authentication
            max_retries: Number of connection retries
            retry_delay: Delay in seconds between retries
        """
        self.contact_points = contact_points
        self.port = port
        self.keyspace = keyspace
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None

    def connect(self, use_system_keyspace: bool = False) -> Session:
        """
        Connect to Cassandra cluster with retry logic.

        Args:
            use_system_keyspace: If True, connect to 'system' keyspace (for schema creation)

        Returns:
            Cassandra session object

        Raises:
            Exception: If unable to connect after max retries
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Connecting to Cassandra (attempt {attempt + 1}/{self.max_retries})..."
                )
                logger.debug(
                    f"  Hosts: {self.contact_points}, Port: {self.port}")

                auth_provider = None
                if self.username and self.password:
                    logger.debug(
                        f"  Using authentication for user: {self.username}")
                    auth_provider = PlainTextAuthProvider(
                        username=self.username,
                        password=self.password
                    )

                self.cluster = Cluster(
                    contact_points=self.contact_points,
                    port=self.port,
                    auth_provider=auth_provider,
                    default_retry_policy=FallthroughRetryPolicy(),
                    protocol_version=4,
                )

                # Determinar a qué conectar
                target_keyspace = None
                if use_system_keyspace:
                    target_keyspace = 'system'
                    logger.debug(
                        "  Connecting to 'system' keyspace for schema creation")
                elif self.keyspace:
                    target_keyspace = self.keyspace
                    logger.debug(f"  Connecting to '{self.keyspace}' keyspace")
                else:
                    logger.debug("  Connecting without specific keyspace")

                # Conectar
                if target_keyspace:
                    self.session = self.cluster.connect(target_keyspace)
                else:
                    self.session = self.cluster.connect()

                logger.info("✓ Successfully connected to Cassandra")
                return self.session

            except Exception as e:
                logger.warning(
                    f"Connection attempt {attempt + 1} failed: {str(e)}"
                )
                logger.debug(f"  Error type: {type(e).__name__}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        "✗ Failed to connect to Cassandra after all retries")
                    raise

    def shutdown(self) -> None:
        """Close Cassandra session and cluster."""
        try:
            if self.session:
                self.session.shutdown()
                logger.info("Session closed")
            if self.cluster:
                self.cluster.shutdown()
                logger.info("Cluster closed")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

    def execute_cql_file(self, file_path: str) -> None:
        """
        Execute CQL statements from a file.

        Args:
            file_path: Path to .cql file

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If CQL execution fails
        """
        if not self.session:
            raise RuntimeError("Not connected to Cassandra")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cql_content = f.read()

            # Split statements by semicolon and filter empty statements
            raw_statements = cql_content.split(';')
            statements = []

            for stmt in raw_statements:
                # Remove comments from start of statement
                lines = stmt.strip().split('\n')
                clean_lines = []
                for line in lines:
                    clean_line = line.strip()
                    # Skip comment-only lines
                    if clean_line and not clean_line.startswith('--'):
                        clean_lines.append(clean_line)

                # Join clean lines
                clean_stmt = ' '.join(clean_lines).strip()

                # Only add non-empty statements
                if clean_stmt:
                    statements.append(clean_stmt)

            logger.info(
                f"Executing {len(statements)} CQL statements from {file_path}")

            for i, statement in enumerate(statements, 1):
                try:
                    # Skip USE statements (they'll be handled after CREATE KEYSPACE)
                    if statement.upper().startswith("USE "):
                        logger.debug(
                            f"  [{i}/{len(statements)}] Skipping USE statement (will reconnect)")
                        continue

                    logger.debug(
                        f"  [{i}/{len(statements)}] {statement[:60]}...")
                    self.session.execute(statement)
                    logger.debug(f"  ✓ Statement {i} executed")

                    # If this was CREATE KEYSPACE, reconnect to the new keyspace
                    if "CREATE KEYSPACE" in statement.upper() and self.keyspace:
                        logger.info(
                            f"  Reconnecting to keyspace '{self.keyspace}'...")
                        self.session.shutdown()
                        self.cluster.shutdown()
                        # Reconnect to the new keyspace
                        self.cluster = Cluster(
                            contact_points=self.contact_points,
                            port=self.port,
                            auth_provider=None,
                            default_retry_policy=FallthroughRetryPolicy(),
                            protocol_version=4,
                        )
                        self.session = self.cluster.connect(self.keyspace)
                        logger.info(
                            f"  ✓ Connected to keyspace '{self.keyspace}'")

                except Exception as e:
                    logger.error(
                        f"✗ Error executing statement {i}: {str(e)}"
                    )
                    logger.error(f"  Statement: {statement}")
                    raise

            logger.info(
                f"✓ All {len(statements)} CQL statements executed successfully")

        except FileNotFoundError:
            logger.error(f"✗ CQL file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"✗ Error executing CQL file: {str(e)}")
            raise

    def get_session(self) -> Session:
        """Get current session."""
        if not self.session:
            raise RuntimeError("Not connected to Cassandra")
        return self.session
