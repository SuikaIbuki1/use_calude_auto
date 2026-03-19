"""
Test Controllers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(__file__).replace("tests/test_controllers.py", "src"))

from controllers import MouseController, KeyboardController


class TestMouseController:
    """Test mouse controller"""
    
    @patch('controllers.mouse_controller.pyautogui')
    def test_get_position(self, mock_pyautogui):
        """Test getting mouse position"""
        mock_pyautogui.position.return_value = (100, 200)
        
        mouse = MouseController()
        pos = mouse.get_position()
        
        assert pos == (100, 200)
        mock_pyautogui.position.assert_called_once()
    
    @patch('controllers.mouse_controller.pyautogui')
    def test_move_to(self, mock_pyautogui):
        """Test moving mouse"""
        mouse = MouseController()
        
        result = mouse.move_to(300, 400)
        
        assert result == True
        mock_pyautogui.moveTo.assert_called_once()
    
    @patch('controllers.mouse_controller.pyautogui')
    def test_click(self, mock_pyautogui):
        """Test mouse click"""
        mouse = MouseController()
        
        result = mouse.click(100, 200, button='left', clicks=1)
        
        assert result == True
        mock_pyautogui.click.assert_called_once()
    
    @patch('controllers.mouse_controller.pyautogui')
    def test_scroll(self, mock_pyautogui):
        """Test mouse scroll"""
        mouse = MouseController()
        
        result = mouse.scroll(100)
        
        assert result == True
        mock_pyautogui.scroll.assert_called_once()


class TestKeyboardController:
    """Test keyboard controller"""
    
    @patch('controllers.keyboard_controller.pyautogui')
    def test_type_text(self, mock_pyautogui):
        """Test typing text"""
        keyboard = KeyboardController()
        
        result = keyboard.type_text("Hello World")
        
        assert result == True
        mock_pyautogui.write.assert_called_once_with("Hello World", interval=0.05)
    
    @patch('controllers.keyboard_controller.pyautogui')
    def test_press_key(self, mock_pyautogui):
        """Test pressing key"""
        keyboard = KeyboardController()
        
        result = keyboard.press_key('enter')
        
        assert result == True
        mock_pyautogui.press.assert_called_once()
    
    @patch('controllers.keyboard_controller.pyautogui')
    def test_hotkey(self, mock_pyautogui):
        """Test hotkey combination"""
        keyboard = KeyboardController()
        
        result = keyboard.hotkey('ctrl', 'c')
        
        assert result == True
        mock_pyautogui.hotkey.assert_called_once()
    
    @patch('controllers.keyboard_controller.pyautogui')
    def test_copy(self, mock_pyautogui):
        """Test copy shortcut"""
        keyboard = KeyboardController()
        
        result = keyboard.copy()
        
        assert result == True
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'c', interval=0.1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])