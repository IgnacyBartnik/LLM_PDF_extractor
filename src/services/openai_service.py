"""
OpenAI service for AI-powered data extraction.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import openai
from openai import OpenAI
import json
import time

from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service."""
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = "gpt-5-nano"
        self.max_retries = 3
        self.retry_delay = 1
    
    def extract_data_from_text(
        self, 
        text: str, 
        extraction_fields: List[str],
        form_type: str = "general",
        model: str = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Extract structured data from text using OpenAI.
        
        Args:
            text: Text content to extract from
            extraction_fields: List of fields to extract
            form_type: Type of form being processed
            model: OpenAI model to use
            temperature: Model temperature for extraction
            
        Returns:
            Dictionary with extraction results
        """
        model = model or self.default_model
        
        # Create extraction prompt
        prompt = self._create_extraction_prompt(text, extraction_fields, form_type)
        
        try:
            response = self._make_api_call(prompt, model, temperature)
            return self._parse_extraction_response(response, extraction_fields)
            
        except Exception as e:
            logger.error(f"Error in data extraction: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_data": {},
                "confidence_scores": {}
            }
    
    def _create_extraction_prompt(
        self, 
        text: str, 
        extraction_fields: List[str], 
        form_type: str
    ) -> str:
        """Create a structured prompt for data extraction."""
        
        fields_str = ", ".join([f'"{field}"' for field in extraction_fields])
        
        prompt = f"""
You are an expert at extracting structured data from {form_type} forms. 

Please extract the following fields from the provided text: {fields_str}

Instructions:
1. Analyze the text carefully and identify the requested information
2. If a field is not found, use "Not found" as the value
3. Return the data in JSON format with the exact field names requested
4. Include confidence scores (0.0 to 1.0) for each extraction
5. Provide brief reasoning for each extraction

Text to analyze:
{text[:8000]}  # Limit text length to avoid token limits

Please respond with a JSON object in this exact format:
{{
    "extracted_data": {{
        "field_name": "extracted_value"
    }},
    "confidence_scores": {{
        "field_name": 0.95
    }},
    "reasoning": {{
        "field_name": "Brief explanation of how this was extracted"
    }}
}}
"""
        return prompt
    
    def _make_api_call(self, prompt: str, model: str, temperature: float) -> str:
        """Make API call to OpenAI with retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a data extraction specialist. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_completion_tokens=2000
                )
                
                return response.choices[0].message.content
                
            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded after all retries")
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"API call failed, retrying... Error: {e}")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e
        
        raise Exception("Failed to make API call after all retries")
    
    def _parse_extraction_response(self, response: str, expected_fields: List[str]) -> Dict[str, Any]:
        """Parse and validate the extraction response."""
        
        try:
            # Try to extract JSON from response
            response_text = response.strip()
            
            # Find JSON content (handle cases where response includes additional text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON content found in response")
            
            json_content = response_text[start_idx:end_idx]
            parsed_response = json.loads(json_content)
            
            # Validate response structure
            if "extracted_data" not in parsed_response:
                raise ValueError("Response missing 'extracted_data' field")
            
            extracted_data = parsed_response.get("extracted_data", {})
            confidence_scores = parsed_response.get("confidence_scores", {})
            reasoning = parsed_response.get("reasoning", {})
            
            # Ensure all expected fields are present
            for field in expected_fields:
                if field not in extracted_data:
                    extracted_data[field] = "Not found"
                if field not in confidence_scores:
                    confidence_scores[field] = 0.0
                if field not in reasoning:
                    reasoning[field] = "Field not found in document"
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "confidence_scores": confidence_scores,
                "reasoning": reasoning,
                "raw_response": response
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON response: {e}",
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Error parsing extraction response: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": response
            }
    
    def validate_api_key(self) -> bool:
        """Validate the OpenAI API key."""
        try:
            # Make a simple API call to test the key
            response = self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return ["gpt-5-nano", "gpt-5-mini", "gpt-5"]  # Fallback to common models
