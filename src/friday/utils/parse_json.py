import json
import re
from typing import Optional, Dict, Any
import logging

def parse_json_from_model(output: str) -> Optional[Dict[Any, Any]]:
    
    if not output or not isinstance(output, str):
        return None
    
    # Step 1: Remove markdown code blocks
    cleaned = re.sub(r"```json\s*(.*?)\s*```", r"\1", output, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"```\s*(.*?)\s*```", r"\1", cleaned, flags=re.DOTALL)
    
    # Step 2: Try to find JSON object within the text
    # Look for content between { and } that might be JSON
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    
    # Step 3: Clean up common formatting issues
    cleaned = cleaned.strip()
    
    # Remove any leading/trailing text that's not part of JSON
    cleaned = re.sub(r'^[^{]*({.*})[^}]*$', r'\1', cleaned, flags=re.DOTALL)
    
    # Step 4: Try parsing the cleaned JSON
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Step 5: Try additional cleanup strategies
        
        # Remove trailing commas
        cleaned_commas = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        try:
            return json.loads(cleaned_commas)
        except json.JSONDecodeError:
            pass
        
        # Try to fix common quote issues
        cleaned_quotes = cleaned.replace("'", '"')
        try:
            return json.loads(cleaned_quotes)
        except json.JSONDecodeError:
            pass
        
        # Try to extract just the content between first { and last }
        start_brace = cleaned.find('{')
        end_brace = cleaned.rfind('}')
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            substring = cleaned[start_brace:end_brace + 1]
            try:
                return json.loads(substring)
            except json.JSONDecodeError:
                pass
        
        # Log the parsing error for debugging
        logging.warning(f"Failed to parse JSON from model output. Error: {e}")
        logging.debug(f"Original output: {output[:500]}...")
        logging.debug(f"Cleaned output: {cleaned[:500]}...")
        
        return None

def extract_json_fields(output: str, required_fields: list) -> Optional[Dict[Any, Any]]:
    
    parsed = parse_json_from_model(output)
    
    if not parsed:
        return None
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in parsed:
            logging.warning(f"Required field '{field}' missing from parsed JSON")
            return None
    
    return parsed

def safe_json_extract(output: str, default_action: str = "generate_action") -> Dict[str, Any]:
    
    parsed = parse_json_from_model(output)
    
    if parsed and isinstance(parsed, dict):
        return parsed
    
    # Return safe default structure
    return {
        "action": default_action,
        "question": output[:500] if isinstance(output, str) else "Failed to parse input",
        "error": "json_parse_failure"
    }