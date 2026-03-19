"""
Decision Engine - Makes intelligent decisions based on screen analysis
"""

import json
from typing import Optional, Dict, Any, List
from PIL import Image
from loguru import logger

from .ai_client import AIClient
from ..recognizers.screen_capture import ScreenCapture
from ..recognizers.ocr_recognizer import OCRRecognizer


class DecisionEngine:
    """
    AI-powered decision engine for automated task execution.
    Analyzes screen content and decides appropriate actions.
    """
    
    def __init__(
        self,
        ai_client: AIClient,
        screen_capture: ScreenCapture,
        ocr_recognizer: Optional[OCRRecognizer] = None,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize decision engine.
        
        Args:
            ai_client: AI client for vision analysis
            screen_capture: Screen capture instance
            ocr_recognizer: OCR recognizer (optional)
            confidence_threshold: Minimum confidence for auto-execution
        """
        self.ai_client = ai_client
        self.screen_capture = screen_capture
        self.ocr_recognizer = ocr_recognizer
        self.confidence_threshold = confidence_threshold
        
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info("DecisionEngine initialized")
    
    def analyze_and_decide(
        self,
        task: str,
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze current screen and decide next action.
        
        Args:
            task: Task description
            context: Additional context
            
        Returns:
            Action decision dict or None
        """
        try:
            # Capture current screen
            screenshot = self.screen_capture.capture_full_screen()
            if not screenshot:
                logger.error("Failed to capture screen")
                return None
            
            # Convert to base64
            import base64
            import io
            buffered = io.BytesIO()
            screenshot.save(buffered, format="JPEG")
            image_data = base64.b64encode(buffered.getvalue()).decode()
            
            # Get OCR text if available
            ocr_text = ""
            if self.ocr_recognizer:
                ocr_text = self.ocr_recognizer.recognize_text(screenshot) or ""
            
            # Build context
            full_context = context or ""
            if ocr_text:
                full_context += f"\n\nOCR Text:\n{ocr_text}"
            
            # Add conversation history
            if self.conversation_history:
                history_str = "\n".join([
                    f"- {item['role']}: {item['content']}"
                    for item in self.conversation_history[-5:]
                ])
                full_context += f"\n\nRecent History:\n{history_str}"
            
            # Define available actions
            available_actions = [
                "click",
                "double_click",
                "right_click",
                "type_text",
                "press_key",
                "hotkey",
                "scroll",
                "wait",
                "drag",
                "move_to"
            ]
            
            # Get AI decision
            decision = self.ai_client.decide_action(
                image_data=image_data,
                task=task,
                available_actions=available_actions,
                context=full_context
            )
            
            if decision:
                # Record in history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": json.dumps(decision)
                })
                
                # Check confidence
                if decision.get("confidence", 0) < self.confidence_threshold:
                    logger.warning(
                        f"Low confidence: {decision['confidence']:.2f} "
                        f"(threshold: {self.confidence_threshold})"
                    )
                    # Could prompt for user confirmation here
                
                return decision
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze and decide: {e}")
            return None
    
    def execute_with_reasoning(
        self,
        task: str,
        max_iterations: int = 10,
        context: Optional[str] = None
    ) -> bool:
        """
        Execute task with iterative AI reasoning.
        
        Args:
            task: Task description
            max_iterations: Maximum iterations
            context: Initial context
            
        Returns:
            True if task completed successfully
        """
        logger.info(f"Starting task: {task}")
        
        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration + 1}/{max_iterations}")
            
            # Analyze and decide
            decision = self.analyze_and_decide(task, context)
            
            if not decision:
                logger.error("Failed to get decision")
                continue
            
            # Check if task is complete
            if decision.get("action") == "complete":
                logger.info("Task completed successfully")
                return True
            
            # Execute action
            action = decision.get("action")
            parameters = decision.get("parameters", {})
            
            logger.info(
                f"Executing: {action} with parameters {parameters}\n"
                f"Reasoning: {decision.get('reasoning')}"
            )
            
            # Record in history
            self.conversation_history.append({
                "role": "user",
                "content": f"Executed {action} with {parameters}"
            })
            
            # Update context
            context = decision.get("reasoning", "")
        
        logger.warning("Max iterations reached")
        return False
    
    def reset_history(self):
        """Reset conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()