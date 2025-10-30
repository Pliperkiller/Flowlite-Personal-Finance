import requests
import json
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from src.application.interfaces.llm_service import LLMService
from src.application.exceptions import LLMServiceError
from src.domain.llm_models import TransactionSummary, LLMRecommendation
from src.domain.prompt_builder import FinancialPromptBuilder

logger = logging.getLogger(__name__)


class OllamaService(LLMService):
    """Ollama implementation of LLM service for local or remote inference"""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
        temperature: float = 0.7,
        timeout: int = 120
    ):
        """
        Initialize Ollama service

        Args:
            host: Ollama API host URL (local or remote, e.g., 'http://192.168.1.100:11434')
            model: Model name to use (e.g., 'llama3.1:8b', 'mistral:7b')
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
        """
        self.host = host.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.generate_url = f"{self.host}/api/generate"
        
        logger.info(f"Initialized OllamaService with model={model}, host={host}")
    
    def _validate_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_ollama(self, prompt: str) -> str:
        """
        Makes a call to Ollama API with retry logic
        
        Args:
            prompt: The complete prompt to send
            
        Returns:
            The generated text response
            
        Raises:
            LLMServiceError: If the API call fails
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature,
            "options": {
                "num_predict": 1000,  # Max tokens to generate
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            logger.info(f"Calling Ollama API with model={self.model}")
            
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '')
            
            if not generated_text:
                raise LLMServiceError("Ollama returned empty response")
            
            logger.info(f"Successfully received response from Ollama ({len(generated_text)} chars)")
            return generated_text
            
        except requests.Timeout:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise LLMServiceError(f"LLM request timed out after {self.timeout} seconds")
        
        except requests.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise LLMServiceError(f"Failed to communicate with Ollama: {str(e)}")
    
    def _parse_llm_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parses the LLM response and extracts JSON
        
        Args:
            response_text: Raw text from LLM
            
        Returns:
            Parsed list of recommendation dictionaries
            
        Raises:
            LLMServiceError: If parsing fails
        """
        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()
            
            # Remove ```json and ``` if present
            if cleaned_text.startswith('```'):
                lines = cleaned_text.split('\n')
                # Remove first and last lines if they are markdown
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned_text = '\n'.join(lines)
            
            # Try to find JSON array in the text
            start_idx = cleaned_text.find('[')
            end_idx = cleaned_text.rfind(']')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON array found in response")
            
            json_text = cleaned_text[start_idx:end_idx + 1]
            
            # Parse JSON
            recommendations = json.loads(json_text)
            
            if not isinstance(recommendations, list):
                raise ValueError("Expected JSON array, got something else")
            
            if not recommendations:
                raise ValueError("LLM returned empty recommendations list")
            
            logger.info(f"Successfully parsed {len(recommendations)} recommendations")
            return recommendations
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            raise LLMServiceError(f"Invalid JSON in LLM response: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise LLMServiceError(f"Failed to parse LLM response: {str(e)}")
    
    def _validate_and_convert_recommendations(
        self, 
        raw_recommendations: List[Dict[str, Any]]
    ) -> List[LLMRecommendation]:
        """
        Validates and converts raw dictionaries to LLMRecommendation objects
        
        Args:
            raw_recommendations: List of dicts from parsed JSON
            
        Returns:
            List of validated LLMRecommendation objects
            
        Raises:
            LLMServiceError: If validation fails
        """
        validated_recommendations = []
        
        for idx, rec in enumerate(raw_recommendations):
            try:
                # Validate required fields
                if not all(key in rec for key in ['category', 'title', 'comment', 'relevance']):
                    logger.warning(f"Recommendation {idx} missing required fields, skipping")
                    continue
                
                # Create LLMRecommendation (will validate internally)
                recommendation = LLMRecommendation(
                    category=rec['category'].lower().strip(),
                    title=rec['title'].strip(),
                    comment=rec['comment'].strip(),
                    relevance=int(rec['relevance'])
                )
                
                validated_recommendations.append(recommendation)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid recommendation {idx}: {e}, skipping")
                continue
        
        if not validated_recommendations:
            raise LLMServiceError("No valid recommendations after validation")
        
        logger.info(f"Validated {len(validated_recommendations)} recommendations")
        return validated_recommendations
    
    def generate_recommendations(
        self,
        transactions: List[TransactionSummary],
        max_insights: int = 5
    ) -> List[LLMRecommendation]:
        """
        Generates financial recommendations based on transaction summaries

        Args:
            transactions: List of aggregated transaction summaries
            max_insights: Maximum number of insights to generate (default: 5)

        Returns:
            List of recommendations generated by the LLM

        Raises:
            LLMServiceError: If generation fails
        """
        if not transactions:
            raise LLMServiceError("Cannot generate recommendations: no transactions provided")

        # Check Ollama connection
        if not self._validate_ollama_connection():
            raise LLMServiceError(
                "Cannot connect to Ollama. Make sure Ollama is running at " + self.host
            )

        # Build prompt
        try:
            prompt = FinancialPromptBuilder.build_complete_prompt(transactions, max_insights)
            logger.debug(f"Built prompt with {len(transactions)} transaction summaries, max_insights={max_insights}")
        except Exception as e:
            raise LLMServiceError(f"Failed to build prompt: {str(e)}")

        # Call LLM
        response_text = self._call_ollama(prompt)

        # Parse response
        raw_recommendations = self._parse_llm_response(response_text)

        # Validate and convert
        recommendations = self._validate_and_convert_recommendations(raw_recommendations)

        return recommendations
