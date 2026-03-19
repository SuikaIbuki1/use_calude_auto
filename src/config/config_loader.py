"""
Config Loader - Loads and manages configuration
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger


class ConfigLoader:
    """
    Configuration loader and manager.
    Supports YAML and JSON formats with environment variable expansion.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config: Dict[str, Any] = {}
        
        if config_path:
            self.load(config_path)
        
        logger.info("ConfigLoader initialized")
    
    def load(self, config_path: str) -> bool:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if successful
        """
        try:
            path = Path(config_path)
            
            if not path.exists():
                logger.error(f"Config file not found: {config_path}")
                return False
            
            content = path.read_text(encoding='utf-8')
            
            # Expand environment variables
            content = os.path.expandvars(content)
            
            if path.suffix in ['.yaml', '.yml']:
                self.config = yaml.safe_load(content)
            elif path.suffix == '.json':
                self.config = json.loads(content)
            else:
                logger.error(f"Unsupported config format: {path.suffix}")
                return False
            
            logger.info(f"Loaded config from {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return False
    
    def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(
        self,
        key: str,
        value: Any
    ):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Set config: {key} = {value}")
    
    def update(self, config_dict: Dict[str, Any]):
        """
        Update configuration with dict.
        
        Args:
            config_dict: Configuration dict to merge
        """
        self._deep_update(self.config, config_dict)
        logger.info("Configuration updated")
    
    def _deep_update(
        self,
        target: Dict[str, Any],
        source: Dict[str, Any]
    ):
        """
        Deep update dictionary.
        
        Args:
            target: Target dictionary
            source: Source dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def save(
        self,
        config_path: str,
        format: str = "yaml"
    ) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_path: Path to save configuration
            format: Output format ('yaml' or 'json')
            
        Returns:
            True if successful
        """
        try:
            path = Path(config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "yaml":
                content = yaml.dump(self.config, default_flow_style=False)
            elif format == "json":
                content = json.dumps(self.config, indent=2)
            else:
                logger.error(f"Unsupported format: {format}")
                return False
            
            path.write_text(content, encoding='utf-8')
            logger.info(f"Saved config to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self.config.copy()