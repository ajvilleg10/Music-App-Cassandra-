"""Configuration module for the application."""
from dataclasses import dataclass
from typing import List, Optional
import os
from pathlib import Path


@dataclass
class CassandraConfig:
    """Cassandra connection configuration."""
    contact_points: List[str]
    keyspace: str
    port: int = 9042
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class AppConfig:
    """Application configuration."""
    cassandra: CassandraConfig
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    max_retries: int = 3


def load_config() -> AppConfig:
    """Load application configuration from environment variables."""
    cassandra_config = CassandraConfig(
        contact_points=os.getenv('CASSANDRA_HOSTS', '127.0.0.1').split(','),
        keyspace=os.getenv('CASSANDRA_KEYSPACE', 'alexvillegas'),
        port=int(os.getenv('CASSANDRA_PORT', '9042')),
        username=os.getenv('CASSANDRA_USERNAME'),
        password=os.getenv('CASSANDRA_PASSWORD')
    )

    return AppConfig(
        cassandra=cassandra_config,
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        log_file=Path(os.getenv('LOG_FILE', 'app.log')
                      ) if os.getenv('LOG_FILE') else None,
        max_retries=int(os.getenv('MAX_RETRIES', '3'))
    )
