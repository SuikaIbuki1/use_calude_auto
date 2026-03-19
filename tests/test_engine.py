"""
Test Task Engine
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import tempfile
import yaml

# Add src to path
sys.path.insert(0, str(__file__).replace("tests/test_engine.py", "src"))

from task_engine import TaskParser, TaskExecutor, StepRunner
from controllers import MouseController, KeyboardController


class TestTaskParser:
    """Test task parser"""
    
    def test_parse_yaml_file(self):
        """Test parsing YAML task file"""
        # Create temporary YAML file
        task_data = {
            'name': 'Test Task',
            'description': 'A test task',
            'mode': 'predefined',
            'steps': [
                {'action': 'click', 'x': 100, 'y': 200}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(task_data, f)
            temp_path = f.name
        
        parser = TaskParser()
        result = parser.parse_file(temp_path)
        
        assert result is not None
        assert result['name'] == 'Test Task'
        assert len(result['steps']) == 1
    
    def test_validate_task(self):
        """Test task validation"""
        parser = TaskParser()
        
        # Valid task
        valid_task = {
            'name': 'Valid Task',
            'steps': [{'action': 'click'}]
        }
        assert parser.validate_task(valid_task) == True
        
        # Invalid task (missing name)
        invalid_task = {'steps': []}
        assert parser.validate_task(invalid_task) == False
    
    def test_parse_simple_task(self):
        """Test parsing simple task description"""
        parser = TaskParser()
        
        result = parser.parse_simple_task("Open notepad and type text")
        
        assert result['name'] == 'Simple Task'
        assert result['mode'] == 'ai_assisted'
        assert 'description' in result


class TestStepRunner:
    """Test step runner"""
    
    @patch('task_engine.step_runner.MouseController')
    @patch('task_engine.step_runner.KeyboardController')
    def test_run_click_step(self, mock_kb, mock_mouse):
        """Test running click step"""
        mock_mouse_instance = Mock()
        mock_mouse_instance.click.return_value = True
        
        runner = StepRunner(mock_mouse_instance, Mock())
        
        step = {
            'action': 'click',
            'x': 100,
            'y': 200
        }
        
        result = runner.run_step(step)
        
        assert result == True
        mock_mouse_instance.click.assert_called_once()
    
    @patch('task_engine.step_runner.MouseController')
    @patch('task_engine.step_runner.KeyboardController')
    def test_run_type_step(self, mock_kb, mock_mouse):
        """Test running type text step"""
        mock_kb_instance = Mock()
        mock_kb_instance.type_text.return_value = True
        
        runner = StepRunner(Mock(), mock_kb_instance)
        
        step = {
            'action': 'type_text',
            'text': 'Hello World'
        }
        
        result = runner.run_step(step)
        
        assert result == True
        mock_kb_instance.type_text.assert_called_once()


class TestTaskExecutor:
    """Test task executor"""
    
    @patch('task_engine.task_executor.MouseController')
    @patch('task_engine.task_executor.KeyboardController')
    def test_execute_predefined_task(self, mock_mouse, mock_kb):
        """Test executing predefined task"""
        mock_mouse_instance = Mock()
        mock_kb_instance = Mock()
        
        executor = TaskExecutor(
            mouse_controller=mock_mouse_instance,
            keyboard_controller=mock_kb_instance
        )
        
        task_def = {
            'name': 'Test Task',
            'mode': 'predefined',
            'steps': [
                {'action': 'wait', 'duration': 0.1}
            ]
        }
        
        result = executor.execute_task(task_def)
        
        assert result == True
    
    @patch('task_engine.task_executor.MouseController')
    @patch('task_engine.task_executor.KeyboardController')
    def test_get_execution_log(self, mock_mouse, mock_kb):
        """Test getting execution log"""
        executor = TaskExecutor()
        
        log = executor.get_execution_log()
        
        assert isinstance(log, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])