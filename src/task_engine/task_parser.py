"""
Task Parser - Parses task definitions from YAML/JSON
"""

import yaml
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger


class TaskParser:
    """
    Parses task definitions from configuration files.
    Supports YAML and JSON formats.
    """
    
    def __init__(self):
        """Initialize task parser."""
        logger.info("TaskParser initialized")
    
    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse task definition from file.
        
        Args:
            file_path: Path to task file (YAML or JSON)
            
        Returns:
            Task definition dict or None if failed
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"Task file not found: {file_path}")
                return None
            
            content = path.read_text(encoding='utf-8')
            
            if path.suffix in ['.yaml', '.yml']:
                task_def = yaml.safe_load(content)
            elif path.suffix == '.json':
                task_def = json.loads(content)
            else:
                logger.error(f"Unsupported file format: {path.suffix}")
                return None
            
            # Validate task definition
            if self.validate_task(task_def):
                logger.info(f"Parsed task: {task_def.get('name', 'Unnamed')}")
                return task_def
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse task file: {e}")
            return None
    
    def parse_string(self, content: str, format: str = "yaml") -> Optional[Dict[str, Any]]:
        """
        Parse task definition from string.
        
        Args:
            content: Task definition string
            format: Format type ('yaml' or 'json')
            
        Returns:
            Task definition dict or None
        """
        try:
            if format == "yaml":
                task_def = yaml.safe_load(content)
            elif format == "json":
                task_def = json.loads(content)
            else:
                logger.error(f"Unsupported format: {format}")
                return None
            
            if self.validate_task(task_def):
                return task_def
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse task string: {e}")
            return None
    
    def validate_task(self, task_def: Dict[str, Any]) -> bool:
        """
        Validate task definition structure.
        
        Args:
            task_def: Task definition dict
            
        Returns:
            True if valid
        """
        required_fields = ['name']
        
        for field in required_fields:
            if field not in task_def:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate steps if present
        if 'steps' in task_def:
            for i, step in enumerate(task_def['steps']):
                if not isinstance(step, dict):
                    logger.error(f"Invalid step {i}: not a dict")
                    return False
                
                if 'action' not in step:
                    logger.error(f"Step {i} missing 'action' field")
                    return False
        
        logger.debug("Task validation passed")
        return True
    
    def parse_simple_task(self, description: str) -> Dict[str, Any]:
        """
        Create a simple task from description.
        
        Args:
            description: Task description
            
        Returns:
            Task definition dict
        """
        return {
            'name': 'Simple Task',
            'description': description,
            'mode': 'ai_assisted',
            'steps': []
        }
    
    def merge_tasks(
        self,
        base_task: Dict[str, Any],
        override_task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two task definitions.
        
        Args:
            base_task: Base task definition
            override_task: Override task definition
            
        Returns:
            Merged task definition
        """
        merged = base_task.copy()
        
        for key, value in override_task.items():
            if key == 'steps' and key in merged:
                # Extend steps list
                merged['steps'].extend(value)
            else:
                merged[key] = value
        
        logger.info("Tasks merged successfully")
        return merged
    
    def extract_parameters(
        self,
        step: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract parameters from step definition.
        
        Args:
            step: Step definition dict
            
        Returns:
            Parameters dict
        """
        params = {}
        
        # Copy all fields except special ones
        exclude_fields = ['action', 'description', 'condition', 'on_error', 'retry']
        
        for key, value in step.items():
            if key not in exclude_fields:
                params[key] = value
        
        return params