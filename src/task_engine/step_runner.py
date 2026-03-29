"""
Step Runner - Executes individual task steps
"""

import time
from typing import Dict, Any, Optional
from loguru import logger

from controllers.mouse_controller import MouseController
from controllers.keyboard_controller import KeyboardController


class StepRunner:
    """
    Executes individual task steps with error handling and retry logic.
    """
    
    def __init__(
        self,
        mouse_controller: MouseController,
        keyboard_controller: KeyboardController,
        default_timeout: float = 30.0,
        default_retries: int = 3
    ):
        """
        Initialize step runner.
        
        Args:
            mouse_controller: Mouse controller instance
            keyboard_controller: Keyboard controller instance
            default_timeout: Default timeout for operations
            default_retries: Default number of retries
        """
        self.mouse = mouse_controller
        self.keyboard = keyboard_controller
        self.default_timeout = default_timeout
        self.default_retries = default_retries
        
        logger.info("StepRunner initialized")
    
    def run_step(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute a single step.
        
        Args:
            step: Step definition dict
            context: Execution context
            
        Returns:
            True if successful
        """
        action = step.get('action')
        
        if not action:
            logger.error("Step missing 'action' field")
            return False
        
        logger.info(f"Running step: {action}")
        
        # Get retry settings
        retries = step.get('retry', self.default_retries)
        
        # Execute with retries
        for attempt in range(retries):
            try:
                success = self._execute_action(action, step)
                
                if success:
                    logger.info(f"Step completed: {action}")
                    return True
                else:
                    logger.warning(
                        f"Step failed (attempt {attempt + 1}/{retries}): {action}"
                    )
                    
                    if attempt < retries - 1:
                        time.sleep(1)
            
            except Exception as e:
                logger.error(
                    f"Step error (attempt {attempt + 1}/{retries}): {e}"
                )
                
                if attempt < retries - 1:
                    time.sleep(1)
        
        logger.error(f"Step failed after {retries} attempts: {action}")
        return False
    
    def _execute_action(
        self,
        action: str,
        params: Dict[str, Any]
    ) -> bool:
        """
        Execute specific action.
        
        Args:
            action: Action name
            params: Action parameters
            
        Returns:
            True if successful
        """
        # Mouse actions
        if action == "click":
            return self.mouse.click(
                x=params.get('x'),
                y=params.get('y'),
                button=params.get('button', 'left'),
                clicks=params.get('clicks', 1)
            )
        
        elif action == "double_click":
            return self.mouse.double_click(
                x=params.get('x'),
                y=params.get('y')
            )
        
        elif action == "right_click":
            return self.mouse.right_click(
                x=params.get('x'),
                y=params.get('y')
            )
        
        elif action == "move_to":
            return self.mouse.move_to(
                x=params['x'],
                y=params['y'],
                duration=params.get('duration')
            )
        
        elif action == "drag":
            return self.mouse.drag_to(
                start_x=params['start_x'],
                start_y=params['start_y'],
                end_x=params['end_x'],
                end_y=params['end_y'],
                duration=params.get('duration', 1.0)
            )
        
        elif action == "scroll":
            return self.mouse.scroll(
                amount=params['amount'],
                x=params.get('x'),
                y=params.get('y')
            )
        
        # Keyboard actions
        elif action == "type_text":
            return self.keyboard.type_text(
                text=params['text'],
                interval=params.get('interval'),
                enter=params.get('enter', False)
            )
        
        elif action == "press_key":
            return self.keyboard.press_key(
                key=params['key'],
                presses=params.get('presses', 1)
            )
        
        elif action == "hotkey":
            keys = params.get('keys', [])
            return self.keyboard.hotkey(*keys)
        
        # Utility actions
        elif action == "wait":
            duration = params.get('duration', 1.0)
            logger.info(f"Waiting for {duration} seconds")
            time.sleep(duration)
            return True
        
        elif action == "copy":
            return self.keyboard.copy()
        
        elif action == "paste":
            return self.keyboard.paste()
        
        elif action == "screenshot":
            return self.keyboard.screenshot(
                save_path=params.get('save_path')
            )
        
        else:
            logger.error(f"Unknown action: {action}")
            return False
    
    def run_step_with_condition(
        self,
        step: Dict[str, Any],
        condition_func
    ) -> bool:
        """
        Run step with condition check.
        
        Args:
            step: Step definition
            condition_func: Function to check condition
            
        Returns:
            True if successful
        """
        # Check condition
        if condition_func():
            logger.info("Condition met, executing step")
            return self.run_step(step)
        else:
            logger.info("Condition not met, skipping step")
            return True
    
    def run_step_on_error(
        self,
        step: Dict[str, Any],
        on_error_step: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Run step with error handler.
        
        Args:
            step: Step definition
            on_error_step: Error handler step
            
        Returns:
            True if successful
        """
        success = self.run_step(step)
        
        if not success and on_error_step:
            logger.warning("Executing error handler")
            return self.run_step(on_error_step)
        
        return success