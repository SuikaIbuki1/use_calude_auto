"""
Image Matcher - Matches images on screen using OpenCV
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple, List
from loguru import logger


class ImageMatcher:
    """
    Image matching module for finding images on screen.
    Uses OpenCV template matching algorithm.
    """
    
    def __init__(self, confidence: float = 0.8):
        """
        Initialize image matcher.
        
        Args:
            confidence: Minimum confidence threshold for matching (0-1)
        """
        self.confidence = confidence
        logger.info(f"ImageMatcher initialized with confidence={confidence}")
    
    def find_image(
        self,
        screen: Image.Image,
        template: Image.Image,
        confidence: Optional[float] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Find template image in screen.
        
        Args:
            screen: Screen PIL Image
            template: Template PIL Image to find
            confidence: Confidence threshold (uses default if None)
            
        Returns:
            Tuple of (x, y, width, height) of matched region or None
        """
        try:
            confidence = confidence or self.confidence
            
            # Convert PIL images to OpenCV format
            screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
            
            # Get template dimensions
            template_height, template_width = template_cv.shape[:2]
            
            # Perform template matching
            result = cv2.matchTemplate(screen_cv, template_cv, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.debug(f"Match confidence: {max_val:.2f}")
            
            if max_val >= confidence:
                # Found a match
                top_left = max_loc
                x, y = top_left
                
                logger.info(
                    f"Found image at ({x}, {y}) "
                    f"with confidence {max_val:.2f}"
                )
                
                return (x, y, template_width, template_height)
            else:
                logger.warning(
                    f"Image not found. Best confidence: {max_val:.2f} "
                    f"(threshold: {confidence})"
                )
                return None
                
        except Exception as e:
            logger.error(f"Failed to find image: {e}")
            return None
    
    def find_all_images(
        self,
        screen: Image.Image,
        template: Image.Image,
        confidence: Optional[float] = None
    ) -> List[Tuple[int, int, int, int]]:
        """
        Find all occurrences of template image in screen.
        
        Args:
            screen: Screen PIL Image
            template: Template PIL Image to find
            confidence: Confidence threshold (uses default if None)
            
        Returns:
            List of tuples (x, y, width, height) for each match
        """
        try:
            confidence = confidence or self.confidence
            
            # Convert PIL images to OpenCV format
            screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
            
            # Get template dimensions
            template_height, template_width = template_cv.shape[:2]
            
            # Perform template matching
            result = cv2.matchTemplate(screen_cv, template_cv, cv2.TM_CCOEFF_NORMED)
            
            # Find all locations above confidence threshold
            locations = np.where(result >= confidence)
            matches = []
            
            for pt in zip(*locations[::-1]):
                x, y = pt
                matches.append((x, y, template_width, template_height))
            
            logger.info(f"Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to find all images: {e}")
            return []
    
    def find_image_center(
        self,
        screen: Image.Image,
        template: Image.Image,
        confidence: Optional[float] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Find center point of template image in screen.
        
        Args:
            screen: Screen PIL Image
            template: Template PIL Image to find
            confidence: Confidence threshold (uses default if None)
            
        Returns:
            Tuple of (x, y) center coordinates or None
        """
        match = self.find_image(screen, template, confidence)
        
        if match:
            x, y, width, height = match
            center_x = x + width // 2
            center_y = y + height // 2
            logger.debug(f"Image center at ({center_x}, {center_y})")
            return (center_x, center_y)
        
        return None
    
    def wait_for_image(
        self,
        screen_capture,
        template: Image.Image,
        timeout: float = 10.0,
        interval: float = 0.5,
        confidence: Optional[float] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Wait for an image to appear on screen.
        
        Args:
            screen_capture: ScreenCapture instance
            template: Template PIL Image to wait for
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
            confidence: Confidence threshold
            
        Returns:
            Match tuple or None if timeout
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            screen = screen_capture.capture_full_screen()
            
            if screen:
                match = self.find_image(screen, template, confidence)
                if match:
                    return match
            
            time.sleep(interval)
        
        logger.warning(f"Image not found within {timeout} seconds")
        return None