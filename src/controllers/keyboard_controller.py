"""
Keyboard Controller - Handles all keyboard operations
"""

import pyautogui
import time
from typing import List, Optional, Union
from loguru import logger


class KeyboardController:
    """
    Keyboard controller for automating keyboard operations.
    Provides safe, high-level keyboard control with typing simulation.
    """
    
    def __init__(
        self,
        typing_speed: float = 0.05,
        safety_delay: float = 0.1,
        fail_safe: bool = True
    ):
        """
        Initialize keyboard controller.
        
        Args:
            typing_speed: Delay between keystrokes in seconds
            safety_delay: Delay between operations
            fail_safe: Enable fail-safe (move mouse to corner to abort)
        """
        self.typing_speed = typing_speed
        self.safety_delay = safety_delay
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = safety_delay
        
        logger.info(f"KeyboardController initialized with typing_speed={typing_speed}")
    
    def type_text(
        self,
        text: str,
        interval: Optional[float] = None,
        enter: bool = False
    ) -> bool:
        """
        Type text character by character.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes (uses default if None)
            enter: Press Enter after typing
            
        Returns:
            True if successful
        """
        try:
            interval = interval or self.typing_speed
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            
            if enter:
                self.press_key("enter")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def press_key(
        self,
        key: str,
        presses: int = 1,
        interval: float = 0.1
    ) -> bool:
        """
        Press a single key.
        
        Args:
            key: Key to press (e.g., 'enter', 'tab', 'space')
            presses: Number of times to press
            interval: Interval between presses
            
        Returns:
            True if successful
        """
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            logger.info(f"Pressed key: {key} ({presses} time(s))")
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            return False
    
    def hotkey(
        self,
        *keys: str,
        interval: float = 0.1
    ) -> bool:
        """
        Press keyboard shortcut (multiple keys simultaneously).
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
            interval: Interval between key presses
            
        Returns:
            True if successful
        """
        try:
            pyautogui.hotkey(*keys, interval=interval)
            logger.info(f"Pressed hotkey: {'+'.join(keys)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to press hotkey {'+'.join(keys)}: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """Hold down a key."""
        try:
            pyautogui.keyDown(key)
            logger.info(f"Key down: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to hold key {key}: {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """Release a key."""
        try:
            pyautogui.keyUp(key)
            logger.info(f"Key up: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to release key {key}: {e}")
            return False
    
    def copy(self) -> bool:
        """Copy to clipboard (Ctrl+C)."""
        return self.hotkey("ctrl", "c")
    
    def paste(self) -> bool:
        """Paste from clipboard (Ctrl+V)."""
        return self.hotkey("ctrl", "v")
    
    def cut(self) -> bool:
        """Cut to clipboard (Ctrl+X)."""
        return self.hotkey("ctrl", "x")
    
    def select_all(self) -> bool:
        """Select all (Ctrl+A)."""
        return self.hotkey("ctrl", "a")
    
    def undo(self) -> bool:
        """Undo (Ctrl+Z)."""
        return self.hotkey("ctrl", "z")
    
    def redo(self) -> bool:
        """Redo (Ctrl+Y or Ctrl+Shift+Z)."""
        return self.hotkey("ctrl", "y")
    
    def save(self) -> bool:
        """Save (Ctrl+S)."""
        return self.hotkey("ctrl", "s")
    
    def find(self) -> bool:
        """Find (Ctrl+F)."""
        return self.hotkey("ctrl", "f")
    
    def screenshot(self, save_path: Optional[str] = None) -> bool:
        """Take screenshot (Windows: Win+PrtSc, Mac: Cmd+Shift+3)."""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            
            if save_path:
                screenshot.save(save_path)
                logger.info(f"Screenshot saved to {save_path}")
            else:
                logger.info("Screenshot taken")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def alt_tab(self, times: int = 1) -> bool:
        """
        Switch windows (Alt+Tab).
        
        Args:
            times: Number of times to press Tab
            
        Returns:
            True if successful
        """
        try:
            pyautogui.keyDown("alt")
            for _ in range(times):
                pyautogui.press("tab")
                time.sleep(0.1)
            pyautogui.keyUp("alt")
            logger.info(f"Alt+Tab pressed {times} time(s)")
            return True
        except Exception as e:
            logger.error(f"Failed to Alt+Tab: {e}")
            return False
    
    def escape(self) -> bool:
        """Press Escape key."""
        return self.press_key("escape")
    
    def enter(self) -> bool:
        """Press Enter key."""
        return self.press_key("enter")
    
    def tab(self) -> bool:
        """Press Tab key."""
        return self.press_key("tab")
    
    def delete(self) -> bool:
        """Press Delete key."""
        return self.press_key("delete")
    
    def backspace(self) -> bool:
        """Press Backspace key."""
        return self.press_key("backspace")
    
    def safe_sleep(self, seconds: float):
        """Sleep with safety check."""
        time.sleep(seconds)