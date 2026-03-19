"""
AI Client - Interfaces with AI APIs for intelligent decisions
"""

import os
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


class AIClient:
    """
    AI client for interacting with OpenAI and Anthropic APIs.
    Supports multiple AI providers with unified interface.
    """
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize AI client.
        
        Args:
            provider: AI provider ('openai' or 'anthropic')
            api_key: API key (uses environment variable if None)
            model: Model to use (uses default if None)
            base_url: Base URL for API (optional)
        """
        self.provider = provider
        
        # Set API key from parameter or environment
        if provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4-vision-preview"
            
            if not openai:
                raise ImportError("openai package not installed")
            
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            
        elif provider == "anthropic":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.model = model or "claude-3-opus-20240229"
            
            if not anthropic:
                raise ImportError("anthropic package not installed")
            
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=base_url
            )
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"AIClient initialized with provider={provider}, model={self.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Optional[str]:
        """
        Send chat message to AI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            AI response text or None if failed
        """
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            elif self.provider == "anthropic":
                # Extract system message if present
                system_message = None
                chat_messages = []
                
                for msg in messages:
                    if msg['role'] == 'system':
                        system_message = msg['content']
                    else:
                        chat_messages.append(msg)
                
                kwargs = {
                    "model": self.model,
                    "messages": chat_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                if system_message:
                    kwargs["system"] = system_message
                
                response = self.client.messages.create(**kwargs)
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"AI chat failed: {e}")
            return None
    
    def chat_with_image(
        self,
        text: str,
        image_data: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Optional[str]:
        """
        Send chat message with image to AI.
        
        Args:
            text: Text message
            image_data: Base64 encoded image data
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            AI response text or None if failed
        """
        try:
            if self.provider == "openai":
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": text
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ]
                
                return self.chat(messages, temperature, max_tokens)
                
            elif self.provider == "anthropic":
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                    }
                ]
                
                return self.chat(messages, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"AI chat with image failed: {e}")
            return None
    
    def analyze_screen(
        self,
        image_data: str,
        task: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Analyze screen content for a specific task.
        
        Args:
            image_data: Base64 encoded screenshot
            task: Task description
            context: Additional context information
            
        Returns:
            AI analysis or None if failed
        """
        prompt = f"Task: {task}\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += (
            "Analyze the screen and provide:\n"
            "1. What you see on the screen\n"
            "2. Relevant elements for the task\n"
            "3. Recommended next action\n\n"
            "Be specific and concise."
        )
        
        return self.chat_with_image(prompt, image_data)
    
    def decide_action(
        self,
        image_data: str,
        task: str,
        available_actions: List[str],
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Decide next action based on screen analysis.
        
        Args:
            image_data: Base64 encoded screenshot
            task: Task description
            available_actions: List of possible actions
            context: Additional context
            
        Returns:
            Dict with action details or None
        """
        import json
        
        prompt = f"Task: {task}\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += (
            f"Available actions: {', '.join(available_actions)}\n\n"
            "Analyze the screen and choose the best action to complete the task.\n"
            "Respond with JSON format:\n"
            "{\n"
            '  "action": "action_name",\n'
            '  "parameters": {},\n'
            '  "reasoning": "why this action",\n'
            '  "confidence": 0.0-1.0\n'
            "}\n\n"
            "Provide ONLY the JSON, no other text."
        )
        
        response = self.chat_with_image(prompt, image_data, temperature=0.3)
        
        if response:
            try:
                # Extract JSON from response
                json_str = response.strip()
                if json_str.startswith("```"):
                    json_str = json_str.split("```")[1]
                    if json_str.startswith("json"):
                        json_str = json_str[4:]
                
                result = json.loads(json_str)
                logger.info(f"AI decided action: {result['action']}")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response: {e}")
                return None
        
        return None