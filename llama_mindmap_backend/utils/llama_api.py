"""Simplified Hugging Face API client for LLM operations."""

import os
import time
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class APIStats:
    """API usage statistics."""
    total_calls: int = 0
    total_response_time: float = 0.0
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        return self.total_response_time / self.total_calls if self.total_calls > 0 else 0.0


class HuggingFaceClient:
    """Simplified Hugging Face API client."""
    
    def __init__(self):
        self._load_config()
        self.stats = APIStats()
        
        if not self.token:
            raise ValueError("HUGGINGFACE_TOKEN not configured")
    
    def _load_config(self) -> None:
        """Load configuration from environment."""
        self.token = os.getenv('HUGGINGFACE_TOKEN', '')
        self.provider = os.getenv('HUGGINGFACE_PROVIDER', 'together')
        self.model = os.getenv('HUGGINGFACE_MODEL', 'deepseek-ai/DeepSeek-R1')
        self.timeout = int(os.getenv('HF_TIMEOUT_SECONDS', '30'))
        self.max_retries = 3
    
    def make_request(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Make request to Hugging Face API.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        url = "https://router.huggingface.co/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "provider": self.provider,
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                
                duration = time.time() - start_time
                self.stats.total_calls += 1
                self.stats.total_response_time += duration
                
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise Exception("Request timed out")
                time.sleep(1 * (attempt + 1))
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    raise Exception("Authentication failed - check token")
                elif e.response.status_code == 402:
                    raise Exception("Billing issue - check credits")
                raise Exception(f"HTTP error: {e}")
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"API error: {e}")
                time.sleep(1 * (attempt + 1))
    
    def parse_list_response(self, response: str, expected_count: int = 5) -> List[str]:
        """Parse response into list of items."""
        import re
        
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        
        cleaned_lines = []
        for line in lines:
            line = line.lstrip('•-*').strip()
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            
            if line:
                cleaned_lines.append(line)
        
        while len(cleaned_lines) < expected_count:
            cleaned_lines.append(f"Additional item {len(cleaned_lines) + 1}")
        
        return cleaned_lines[:expected_count]


# Global client instance
_client: Optional[HuggingFaceClient] = None


def get_client() -> HuggingFaceClient:
    """Get or create global client instance."""
    global _client
    if _client is None:
        _client = HuggingFaceClient()
    return _client


def expand_topic(topic: str) -> List[str]:
    """Expand topic into subtopics."""
    client = get_client()
    
    prompt = f"""Break down the following task into exactly 5 smaller, actionable sub-tasks.
Each sub-task must be distinct, specific, and contribute to completing the main task.

Task: {topic}

Return exactly 5 sub-tasks, one per line, without numbering or bullet points."""

    try:
        response = client.make_request(prompt, max_tokens=200)
        return client.parse_list_response(response, 5)
    except Exception as e:
        logger.error(f"Expand topic failed for '{topic}': {e}")
        return [
            f"Research and planning for {topic}",
            f"Preparation and setup for {topic}",
            f"Implementation of {topic}",
            f"Testing and validation of {topic}",
            f"Completion and review of {topic}"
        ]


def breakdown_topic(topic: str) -> List[str]:
    """Break down topic into actionable steps."""
    client = get_client()
    
    prompt = f"""Create exactly 5 clear, actionable steps to complete the following task.
Each step should be practical and easy to follow.

Task: {topic}

Return exactly 5 steps, one per line, without numbering or bullet points."""

    try:
        response = client.make_request(prompt, max_tokens=250)
        return client.parse_list_response(response, 5)
    except Exception as e:
        logger.error(f"Breakdown topic failed for '{topic}': {e}")
        return [
            f"Plan and research {topic}",
            f"Gather necessary resources for {topic}",
            f"Begin implementation of {topic}",
            f"Complete the main work for {topic}",
            f"Review and finalize {topic}"
        ]


def analyze_topic(topic: str) -> str:
    """Provide analysis of a topic."""
    client = get_client()
    
    prompt = f"""Analyze the following task in no more than 100 words.
Identify the core objective, key requirements, and potential challenges.

Task: {topic}

Return a single paragraph analysis."""

    try:
        response = client.make_request(prompt, max_tokens=150)
        return response.strip() or f"Analysis of {topic}: This task requires careful planning and execution."
    except Exception as e:
        logger.error(f"Analyze topic failed for '{topic}': {e}")
        return f"Analysis of {topic}: This task requires systematic approach and careful execution."


def test_api_connection() -> bool:
    """Test API connection."""
    try:
        client = get_client()
        result = client.make_request("Respond with 'connection test successful'", max_tokens=30)
        return "successful" in result.lower() or "connection" in result.lower()
    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        return False


def get_api_stats() -> dict:
    """Get API usage statistics."""
    try:
        client = get_client()
        return {
            "total_calls": client.stats.total_calls,
            "total_response_time": client.stats.total_response_time,
            "average_response_time": client.stats.average_response_time,
            "using_huggingface": True,
            "endpoint": "Hugging Face Inference Providers",
            "model": client.model,
            "provider": client.provider,
            "token_configured": bool(client.token)
        }
    except Exception:
        return {
            "total_calls": 0,
            "total_response_time": 0.0,
            "average_response_time": 0.0,
            "using_huggingface": False,
            "error": "Client not initialized"
        }