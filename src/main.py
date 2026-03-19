"""
AI Auto Operator - Main Entry Point
Intelligent mouse and keyboard automation system
"""

import click
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from controllers import MouseController, KeyboardController
from recognizers import ScreenCapture, ImageMatcher, OCRRecognizer
from ai_engine import AIClient, DecisionEngine
from task_engine import TaskExecutor, TaskParser
from config import ConfigLoader
from utils import setup_logger


# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="0.1.0", prog_name="ai-auto-operator")
def cli():
    """AI Auto Operator - Intelligent automation system"""
    setup_logger()
    logger.info("AI Auto Operator started")


@cli.command()
@click.argument('task_file', type=click.Path(exists=True))
@click.option('--config', '-c', default='config/config.yaml', help='Config file path')
@click.option('--dry-run', is_flag=True, help='Show execution plan without running')
def run(task_file: str, config: str, dry_run: bool):
    """Execute task from file"""
    logger.info(f"Executing task from: {task_file}")
    
    # Load configuration
    config_loader = ConfigLoader()
    if Path(config).exists():
        config_loader.load(config)
    
    # Initialize components
    mouse = MouseController(
        safety_delay=config_loader.get('mouse.safety_delay', 0.1),
        move_duration=config_loader.get('mouse.move_duration', 0.5)
    )
    
    keyboard = KeyboardController(
        typing_speed=config_loader.get('keyboard.typing_speed', 0.05)
    )
    
    screen_capture = ScreenCapture()
    
    # Initialize AI client if needed
    decision_engine = None
    ai_enabled = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    
    if ai_enabled:
        try:
            ai_client = AIClient(
                provider=config_loader.get('ai.provider', 'openai'),
                model=config_loader.get('ai.model')
            )
            
            ocr = OCRRecognizer(
                backend=config_loader.get('recognition.ocr_backend', 'tesseract'),
                language=config_loader.get('recognition.ocr_language', 'chi_sim+eng')
            )
            
            decision_engine = DecisionEngine(
                ai_client=ai_client,
                screen_capture=screen_capture,
                ocr_recognizer=ocr,
                confidence_threshold=config_loader.get('ai.confidence_threshold', 0.7)
            )
            
            logger.info("AI engine initialized")
            
        except Exception as e:
            logger.warning(f"AI engine not available: {e}")
    
    # Create task executor
    executor = TaskExecutor(
        mouse_controller=mouse,
        keyboard_controller=keyboard,
        decision_engine=decision_engine
    )
    
    if dry_run:
        # Parse and show task without executing
        parser = TaskParser()
        task_def = parser.parse_file(task_file)
        
        if task_def:
            click.echo("\n" + "="*60)
            click.echo("Task Execution Plan")
            click.echo("="*60)
            click.echo(f"\nName: {task_def.get('name')}")
            click.echo(f"Description: {task_def.get('description')}")
            click.echo(f"Mode: {task_def.get('mode', 'predefined')}")
            
            steps = task_def.get('steps', [])
            if steps:
                click.echo(f"\nSteps ({len(steps)}):")
                for i, step in enumerate(steps, 1):
                    click.echo(f"  {i}. {step.get('action')} - {step.get('description', '')}")
            
            click.echo("\n" + "="*60)
        else:
            click.echo("Failed to parse task file", err=True)
    else:
        # Execute task
        success = executor.execute_from_file(task_file)
        
        if success:
            click.echo(click.style("\n✓ Task completed successfully!", fg='green', bold=True))
        else:
            click.echo(click.style("\n✗ Task execution failed!", fg='red', bold=True), err=True)
            raise click.Abort()


@cli.command()
@click.argument('description')
@click.option('--config', '-c', default='config/config.yaml', help='Config file path')
@click.option('--iterations', '-i', default=10, help='Maximum iterations')
def ask(description: str, config: str, iterations: int):
    """Execute simple task with AI assistance"""
    logger.info(f"Executing AI-assisted task: {description}")
    
    # Check AI availability
    if not (os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')):
        click.echo(click.style("Error: No API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY", fg='red'), err=True)
        raise click.Abort()
    
    # Load configuration
    config_loader = ConfigLoader()
    if Path(config).exists():
        config_loader.load(config)
    
    # Initialize components
    mouse = MouseController()
    keyboard = KeyboardController()
    screen_capture = ScreenCapture()
    
    ai_client = AIClient(
        provider=config_loader.get('ai.provider', 'openai'),
        model=config_loader.get('ai.model')
    )
    
    ocr = OCRRecognizer(
        backend=config_loader.get('recognition.ocr_backend', 'tesseract'),
        language=config_loader.get('recognition.ocr_language', 'chi_sim+eng')
    )
    
    decision_engine = DecisionEngine(
        ai_client=ai_client,
        screen_capture=screen_capture,
        ocr_recognizer=ocr,
        confidence_threshold=config_loader.get('ai.confidence_threshold', 0.7)
    )
    
    executor = TaskExecutor(
        mouse_controller=mouse,
        keyboard_controller=keyboard,
        decision_engine=decision_engine
    )
    
    # Execute with AI assistance
    click.echo(click.style(f"\nStarting AI-assisted task: {description}", fg='cyan', bold=True))
    click.echo("The AI will analyze your screen and perform actions...\n")
    
    success = executor.execute_simple(description, max_iterations=iterations)
    
    if success:
        click.echo(click.style("\n✓ Task completed successfully!", fg='green', bold=True))
    else:
        click.echo(click.style("\n✗ Task execution failed!", fg='red', bold=True), err=True)


@cli.command()
def test():
    """Test mouse and keyboard controllers"""
    click.echo(click.style("\nTesting Mouse Controller...", fg='cyan', bold=True))
    
    mouse = MouseController()
    
    # Get current position
    x, y = mouse.get_position()
    click.echo(f"Current mouse position: ({x}, {y})")
    
    click.echo(click.style("\nTesting Keyboard Controller...", fg='cyan', bold=True))
    
    keyboard = KeyboardController()
    
    click.echo("Typing test in 3 seconds...")
    import time
    time.sleep(3)
    
    keyboard.type_text("Hello from AI Auto Operator!", enter=True)
    
    click.echo(click.style("\n✓ Test completed!", fg='green', bold=True))


@cli.command()
def screen():
    """Capture current screen"""
    click.echo(click.style("\nCapturing screen...", fg='cyan', bold=True))
    
    capture = ScreenCapture()
    
    # Save to screenshots directory
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    save_path = f"screenshots/screen_{timestamp}.png"
    
    Path("screenshots").mkdir(exist_ok=True)
    
    screenshot = capture.capture_full_screen(save_path)
    
    if screenshot:
        click.echo(click.style(f"\n✓ Screenshot saved to: {save_path}", fg='green', bold=True))
    else:
        click.echo(click.style("\n✗ Failed to capture screen", fg='red'), err=True)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
def find(image_path: str):
    """Find image on screen"""
    click.echo(click.style(f"\nFinding image: {image_path}", fg='cyan', bold=True))
    
    from PIL import Image
    
    capture = ScreenCapture()
    matcher = ImageMatcher()
    
    # Load template
    template = Image.open(image_path)
    
    # Capture screen
    screen_img = capture.capture_full_screen()
    
    # Find image
    result = matcher.find_image_center(screen_img, template)
    
    if result:
        x, y = result
        click.echo(click.style(f"\n✓ Found at position: ({x}, {y})", fg='green', bold=True))
        
        # Move mouse to position
        mouse = MouseController()
        mouse.move_to(x, y)
        click.echo(f"Mouse moved to ({x}, {y})")
    else:
        click.echo(click.style("\n✗ Image not found on screen", fg='yellow'))


if __name__ == '__main__':
    cli()