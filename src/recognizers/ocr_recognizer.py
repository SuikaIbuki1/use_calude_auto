"""
OCR Recognizer - Text recognition from images
"""

import pytesseract
from PIL import Image
from typing import Optional, List, Dict, Any
from loguru import logger


class OCRRecognizer:
    """
    OCR (Optical Character Recognition) module.
    Supports both Tesseract and EasyOCR backends.
    """
    
    def __init__(
        self,
        backend: str = "tesseract",
        language: str = "chi_sim+eng",
        tesseract_cmd: Optional[str] = None
    ):
        """
        Initialize OCR recognizer.
        
        Args:
            backend: OCR backend ('tesseract' or 'easyocr')
            language: Language for OCR (e.g., 'chi_sim' for Chinese, 'eng' for English)
            tesseract_cmd: Path to tesseract executable (Windows only)
        """
        self.backend = backend
        self.language = language
        self.easyocr_reader = None
        
        # Set tesseract command path (Windows)
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Initialize EasyOCR if needed
        if backend == "easyocr":
            try:
                import easyocr
                lang_list = language.split('+')
                self.easyocr_reader = easyocr.Reader(lang_list, gpu=False)
                logger.info(f"EasyOCR initialized with languages: {lang_list}")
            except ImportError:
                logger.warning("EasyOCR not installed, falling back to Tesseract")
                self.backend = "tesseract"
        
        logger.info(f"OCRRecognizer initialized with backend={backend}, language={language}")
    
    def recognize_text(
        self,
        image: Image.Image,
        language: Optional[str] = None
    ) -> Optional[str]:
        """
        Recognize text from image.
        
        Args:
            image: PIL Image to recognize
            language: Language for OCR (uses default if None)
            
        Returns:
            Recognized text or None if failed
        """
        try:
            language = language or self.language
            
            if self.backend == "tesseract":
                text = pytesseract.image_to_string(image, lang=language)
            else:  # easyocr
                import numpy as np
                result = self.easyocr_reader.readtext(np.array(image))
                text = '\n'.join([item[1] for item in result])
            
            text = text.strip()
            logger.info(f"Recognized text: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"Failed to recognize text: {e}")
            return None
    
    def recognize_with_positions(
        self,
        image: Image.Image,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recognize text with position information.
        
        Args:
            image: PIL Image to recognize
            language: Language for OCR
            
        Returns:
            List of dicts with text and position info
        """
        try:
            language = language or self.language
            
            if self.backend == "tesseract":
                data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
                
                results = []
                for i in range(len(data['text'])):
                    if data['text'][i].strip():
                        results.append({
                            'text': data['text'][i],
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i],
                            'confidence': data['conf'][i]
                        })
                
                logger.info(f"Found {len(results)} text elements")
                return results
                
            else:  # easyocr
                import numpy as np
                result = self.easyocr_reader.readtext(np.array(image))
                
                results = []
                for item in result:
                    bbox, text, confidence = item
                    x, y, w, h = self._bbox_to_coords(bbox)
                    results.append({
                        'text': text,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'confidence': confidence
                    })
                
                logger.info(f"Found {len(results)} text elements")
                return results
                
        except Exception as e:
            logger.error(f"Failed to recognize text with positions: {e}")
            return []
    
    def find_text(
        self,
        image: Image.Image,
        search_text: str,
        language: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find specific text in image.
        
        Args:
            image: PIL Image to search
            search_text: Text to find
            language: Language for OCR
            
        Returns:
            Dict with text and position or None
        """
        results = self.recognize_with_positions(image, language)
        
        for result in results:
            if search_text.lower() in result['text'].lower():
                logger.info(f"Found text '{search_text}' at ({result['x']}, {result['y']})")
                return result
        
        logger.warning(f"Text '{search_text}' not found")
        return None
    
    def _bbox_to_coords(self, bbox: List[List[int]]) -> tuple:
        """
        Convert EasyOCR bbox to standard coordinates.
        
        Args:
            bbox: List of corner points
            
        Returns:
            Tuple of (x, y, width, height)
        """
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        
        x = int(min(x_coords))
        y = int(min(y_coords))
        width = int(max(x_coords) - x)
        height = int(max(y_coords) - y)
        
        return (x, y, width, height)
    
    def get_text_center(
        self,
        image: Image.Image,
        search_text: str,
        language: Optional[str] = None
    ) -> Optional[tuple]:
        """
        Find center position of specific text.
        
        Args:
            image: PIL Image to search
            search_text: Text to find
            language: Language for OCR
            
        Returns:
            Tuple of (x, y) center coordinates or None
        """
        result = self.find_text(image, search_text, language)
        
        if result:
            center_x = result['x'] + result['width'] // 2
            center_y = result['y'] + result['height'] // 2
            return (center_x, center_y)
        
        return None