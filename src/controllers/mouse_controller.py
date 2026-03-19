"""
Mouse Controller - Handles all mouse operations
"""

import pyautogui
import time
from typing import Tuple, Optional
from loguru import logger


class MouseController:
    """
    Mouse controller for automating mouse operations.
    Provides safe, high-level mouse control with safety features.
    """
    
    def __init__(
        self,
        safety_delay: float = 0.1,
        move_duration: float = 0.5,
        fail_safe: bool = True
    ):
        """
        Initialize mouse controller with safety settings.
        
        Args:
            safety_delay: Delay between operations in seconds
            move_duration: Default duration for mouse movements
            fail_safe: Enable fail-safe (move mouse to corner to abort)
        """
        self.safety_delay = safety_delay
        self.move_duration = move_duration
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = safety_delay
        
        logger.info(f"MouseController initialized with fail_safe={fail_safe}")
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        pos = pyautogui.position()
        logger.debug(f"Current mouse position: {pos}")
        return pos
    
    def move_to(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None,
        relative: bool = False
    ) -> bool:
        """
        Move mouse to specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration (uses default if None)
            relative: If True, move relative to current position
            
        Returns:
            True if successful
        """
        try:
            duration = duration or self.move_duration
            
            if relative:
                current_x, current_y = self.get_position()
                x += current_x
                y += current_y
            
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False
    
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        clicks: int = 1,
        duration: Optional[float] = None
    ) -> bool:
        """
        Click at specified position or current position.
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            duration: Duration before click
            
        Returns:
            True if successful
        """
        try:
            duration = duration or self.move_duration
            
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button, duration=duration)
                logger.info(f"Clicked {button} button {clicks} time(s) at ({x}, {y})")
            else:
                pyautogui.click(clicks=clicks, button=button)
                pos = self.get_position()
                logger.info(f"Clicked {button} button {clicks} time(s) at current position {pos}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False
    
    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        duration: Optional[float] = None
    ) -> bool:
        """Double click at specified position."""
        return self.click(x, y, button="left", clicks=2, duration=duration)
    
    def right_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        duration: Optional[float] = None
    ) -> bool:
        """Right click at specified position."""
        return self.click(x, y, button="right", duration=duration)
    
    def drag_to(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 1.0,
        button: str = "left"
    ) -> bool:
        """
        Drag from start position to end position.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Drag duration
            button: Mouse button to hold during drag
            
        Returns:
            True if successful
        """
        try:
            # Move to start position
            pyautogui.moveTo(start_x, start_y, duration=duration/2)
            
            # Drag to end position
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration/2, button=button)
            
            logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drag: {e}")
            return False
    
    def scroll(
        self,
        amount: int,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> bool:
        """
        Scroll the mouse wheel.
        
        Args:
            amount: Scroll amount (positive for up, negative for down)
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            
        Returns:
            True if successful
        """
        try:
            if x is not None and y is not None:
                pyautogui.scroll(amount, x, y)
                logger.info(f"Scrolled {amount} at ({x}, {y})")
            else:
                pyautogui.scroll(amount)
                logger.info(f"Scrolled {amount}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False
    
    def hover(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None
    ) -> bool:
        """Move mouse to position and wait."""
        return self.move_to(x, y, duration)
    
    def safe_sleep(self, seconds: float):
        """Sleep with safety check."""
        time.sleep(seconds)