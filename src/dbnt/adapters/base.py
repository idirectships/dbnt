"""Base adapter interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from dbnt.core import Rule


class BaseAdapter(ABC):
    """Base class for DBNT adapters."""

    @abstractmethod
    def install(self) -> None:
        """Install DBNT into the target system."""
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """Remove DBNT from the target system."""
        pass

    @abstractmethod
    def get_rules_path(self) -> Path:
        """Get the path where rules should be stored."""
        pass

    @abstractmethod
    def sync_rule(self, rule: Rule) -> None:
        """Sync a rule to the target system's format."""
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if DBNT is installed in the target system."""
        pass
