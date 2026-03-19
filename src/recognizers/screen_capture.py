"""
Screen Capture - Captures screen screenshots
"""

import pyautogui
from PIL import Image
from typing import Optional, Tuple
from loguru import logger


class ScreenCapture:
    """
    Screen capture module for taking screenshots.
    Supports full screen and region capture.
    """
    
    def __init__(self):
        """Initialize screen capture."""
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
    
    def capture_full_screen(
        self,
        save_path: Optional[str] = None
    ) -> Optional[Image.Image]:
        """
        Capture full screen.
        
        Args:
            save_path: Path to save screenshot (optional)
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            screenshot = pyautogui.screenshot()
            logger.info("Captured full screen")
            
            if save_path:
                screenshot.save(save_path)
                logger.info(f"Screenshot saved to {save_path}")
            
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None
    
    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        save_path: Optional[str] = None
    ) -> Optional[Image.Image]:
        """
        Capture a specific region of the screen.
        
        Args:
            x: X coordinate of region
            y: Y coordinate of region
            width: Width of region
            height: Height of region
            save_path: Path to save screenshot (optional)
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            region = (x, y, width, height)
            screenshot = pyautogui.screenshot(region=region)
            logger.info(f"Captured region: x={x}, y={y}, width={width}, height={height}")
            
            if save_path:
                screenshot.save(save_path)
                logger.info(f"Region screenshot saved to {save_path}")
            
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to capture region: {e}")
            return None
    
    def capture_around_point(
        self,
        x: int,
        y: int,
        radius: int,
        save_path: Optional[str] = None
    ) -> Optional[Image.Image]:
        """
        Capture screen around a specific point.
        
        Args:
            x: X coordinate of center point
            y: Y coordinate of center point
            radius: Radius around the point
            save_path: Path to save screenshot (optional)
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            # Calculate region bounds
            left = max(0, x - radius)
            top = max(0, y - radius)
            right = min(self.screen_width, x + radius)
            bottom = min(self.screen_height, y + radius)
            
            width = right - left
            height = bottom - top
            
            return self.capture_region(left, top, width, height, save_path)
            
        except Exception as e:
            logger.error(f"Failed to capture around point: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen resolution."""
        return (self.screen_width, self.screen_height)
    
    def pixel_at(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        Get pixel color at specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            RGB tuple or None if failed
        """
        try:
            pixel = pyautogui.pixel(x, y)
            logger.debug(f"Pixel at ({x}, {y}): {pixel}")
            return pixel
        except Exception as e:
            logger.error(f"Failed to get pixel: {e}")
            return None