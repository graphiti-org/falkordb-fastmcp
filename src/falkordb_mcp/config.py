"""Configuration management for FalkorDB MCP server."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class FalkorDBConfig:
    """FalkorDB connection configuration."""

    host: str
    port: int
    username: Optional[str]
    password: Optional[str]

    @classmethod
    def from_env(cls) -> "FalkorDBConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("FALKORDB_HOST", "localhost"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
            username=os.getenv("FALKORDB_USERNAME") or None,
            password=os.getenv("FALKORDB_PASSWORD") or None,
        )


# Global configuration instance
config = FalkorDBConfig.from_env()
