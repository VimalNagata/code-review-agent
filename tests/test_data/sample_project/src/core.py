"""Core module for sample project."""
from typing import List, Dict, Any, Optional

class BaseModel:
    """Base class for models."""
    
    def __init__(self, name: str):
        """Initialize with a name."""
        self.name = name
        
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name})"


class ConfigManager:
    """Manages configuration for the application."""
    
    def __init__(self, config_path: str = None):
        """Initialize with config path."""
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration."""
        # In a real implementation, this would load from a file
        self._config = {"version": "1.0", "debug": True}
        return self._config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)


def initialize_app(config_path: Optional[str] = None) -> ConfigManager:
    """Initialize the application."""
    config = ConfigManager(config_path)
    config.load()
    return config