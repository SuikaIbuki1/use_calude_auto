"""
Task Executor - Orchestrates task execution
"""

import time
from typing import Dict, Any, Optional, List
from loguru import logger

from .task_parser import TaskParser
from .step_runner import StepRunner
from ..controllers.mouse_controller import MouseController
from ..controllers.keyboard_controller import KeyboardController
from ..ai_engine.decision_engine import DecisionEngine
from ..recognizers.screen_capture import ScreenCapture


class TaskExecutor:
    """
    Main task executor that orchestrates the entire execution flow.
    Supports both predefined steps and AI-assisted execution.
    """
    
    def __init__(
        self,
        mouse_controller: Optional[MouseController] = None,
        keyboard_controller: Optional[KeyboardController] = None,
        decision_engine: Optional[DecisionEngine] = None,
        step_runner: Optional[StepRunner] = None,
        task_parser: Optional[TaskParser] = None
    ):
        """
        Initialize task executor.
        
        Args:
            mouse_controller: Mouse controller (created if None)
            keyboard_controller: Keyboard controller (created if None)
            decision_engine: AI decision engine (optional)
            step_runner: Step runner (created if None)
            task_parser: Task parser (created if None)
        """
        # Initialize controllers
        self.mouse = mouse_controller or MouseController()
        self.keyboard = keyboard_controller or KeyboardController()
        
        # Initialize components
        self.decision_engine = decision_engine
        self.step_runner = step_runner or StepRunner(self.mouse, self.keyboard)
        self.task_parser = task_parser or TaskParser()
        
        # Execution state
        self.current_task = None
        self.execution_log: List[Dict[str, Any]] = []
        
        logger.info("TaskExecutor initialized")
    
    def execute_task(
        self,
        task_definition: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute a task from definition.
        
        Args:
            task_definition: Task definition dict
            context: Execution context
            
        Returns:
            True if task completed successfully
        """
        logger.info(f"Executing task: {task_definition.get('name', 'Unnamed')}")
        
        self.current_task = task_definition
        self.execution_log = []
        
        try:
            # Get execution mode
            mode = task_definition.get('mode', 'predefined')
            
            if mode == 'ai_assisted':
                return self._execute_ai_assisted(task_definition, context)
            elif mode == 'predefined':
                return self._execute_predefined(task_definition, context)
            elif mode == 'hybrid':
                return self._execute_hybrid(task_definition, context)
            else:
                logger.error(f"Unknown execution mode: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return False
    
    def execute_from_file(
        self,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute task from file.
        
        Args:
            file_path: Path to task file
            context: Execution context
            
        Returns:
            True if successful
        """
        task_def = self.task_parser.parse_file(file_path)
        
        if task_def:
            return self.execute_task(task_def, context)
        
        return False
    
    def execute_simple(
        self,
        description: str,
        max_iterations: int = 10
    ) -> bool:
        """
        Execute simple task from description (AI-assisted).
        
        Args:
            description: Task description
            max_iterations: Maximum iterations
            
        Returns:
            True if successful
        """
        if not self.decision_engine:
            logger.error("Decision engine not available")
            return False
        
        logger.info(f"Executing simple task: {description}")
        
        return self.decision_engine.execute_with_reasoning(
            task=description,
            max_iterations=max_iterations
        )
    
    def _execute_predefined(
        self,
        task_def: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Execute predefined step sequence.
        
        Args:
            task_def: Task definition
            context: Execution context
            
        Returns:
            True if successful
        """
        steps = task_def.get('steps', [])
        
        if not steps:
            logger.warning("No steps defined in task")
            return True
        
        for i, step in enumerate(steps):
            logger.info(f"Executing step {i + 1}/{len(steps)}")
            
            # Check condition if present
            if 'condition' in step:
                # Condition check would be implemented based on specific needs
                logger.debug(f"Checking condition: {step['condition']}")
            
            # Execute step
            success = self.step_runner.run_step(step, context)
            
            # Log execution
            self.execution_log.append({
                'step': i,
                'action': step.get('action'),
                'success': success
            })
            
            # Handle failure
            if not success:
                on_error = step.get('on_error', 'abort')
                
                if on_error == 'abort':
                    logger.error("Aborting task due to step failure")
                    return False
                elif on_error == 'skip':
                    logger.warning("Skipping failed step")
                    continue
                elif on_error == 'retry':
                    logger.info("Retrying step")
                    success = self.step_runner.run_step(step, context)
                    if not success:
                        return False
            
            # Delay between steps
            delay = step.get('delay', 0.5)
            if delay > 0:
                time.sleep(delay)
        
        logger.info("Task completed successfully")
        return True
    
    def _execute_ai_assisted(
        self,
        task_def: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Execute task with AI assistance.
        
        Args:
            task_def: Task definition
            context: Execution context
            
        Returns:
            True if successful
        """
        if not self.decision_engine:
            logger.error("Decision engine not available for AI-assisted mode")
            return False
        
        description = task_def.get('description', '')
        max_iterations = task_def.get('max_iterations', 10)
        
        return self.decision_engine.execute_with_reasoning(
            task=description,
            max_iterations=max_iterations,
            context=str(context) if context else None
        )
    
    def _execute_hybrid(
        self,
        task_def: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Execute hybrid task (predefined steps + AI fallback).
        
        Args:
            task_def: Task definition
            context: Execution context
            
        Returns:
            True if successful
        """
        # Try predefined steps first
        success = self._execute_predefined(task_def, context)
        
        # If failed and AI available, try AI-assisted
        if not success and self.decision_engine:
            logger.info("Predefined execution failed, trying AI-assisted mode")
            return self._execute_ai_assisted(task_def, context)
        
        return success
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution log."""
        return self.execution_log.copy()
    
    def stop(self):
        """Stop current task execution."""
        logger.warning("Task execution stop requested")
        # Could implement a stop flag here for long-running tasks