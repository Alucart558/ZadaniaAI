import requests
import re
import json
from typing import Dict, Any

class DataCensoringSystem:
    def __init__(self, api_endpoint: str = "https://centrala.ag3nts.org/report"):
        self.api_endpoint = api_endpoint
        
    def download_data(self, url: str) -> str:
        """Download data from the specified URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to download data: {e}")
    
    def censor_personal_info(self, text: str) -> str:
        """Censor personal information in the text."""
        # Censor email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'CENZURA', text)
        
        # Censor phone numbers (various formats)
        text = re.sub(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', 'CENZURA', text)
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'CENZURA', text)
        text = re.sub(r'\b\d{10}\b', 'CENZURA', text)
        
        # Censor credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'CENZURA', text)
        
        # Censor social security numbers
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'CENZURA', text)
        
        # Censor addresses (basic pattern)
        text = re.sub(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b', 'CENZURA', text, flags=re.IGNORECASE)
        
        # Censor names (assuming format: First Last or First Middle Last)
        text = re.sub(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', 'CENZURA', text)
        
        return text
    
    def send_to_api(self, censored_data: str, task_name: str = "CENZURA", api_key: str = None) -> Dict[str, Any]:
        """Send censored data to the API."""
        payload = {
            "task": task_name,
            "apikey": api_key,
            "answer": censored_data
        }
        
        try:
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to send data to API: {e}")
    
    def process_data(self, data_url: str, api_key: str, task_name: str = "CENZURA") -> Dict[str, Any]:
        """Complete data processing pipeline."""
        # Download data
        raw_data = self.download_data(data_url)
        
        # Censor personal information
        censored_data = self.censor_personal_info(raw_data)
        
        # Send to API
        result = self.send_to_api(censored_data, task_name, api_key)
        
        return {
            "original_length": len(raw_data),
            "censored_length": len(censored_data),
            "api_response": result
        }

# Example usage
if __name__ == "__main__":
    # Initialize the censoring system
    censoring_system = DataCensoringSystem()
    
    # Configuration
    DATA_URL = "https://centrala.ag3nts.org/data/YOUR_API_KEY/cenzura.txt"
    API_KEY = "YOUR_API_KEY"
    
    try:
        # Process the data
        result = censoring_system.process_data(DATA_URL, API_KEY)
        
        print("Data processing completed successfully!")
        print(f"Original data length: {result['original_length']} characters")
        print(f"Censored data length: {result['censored_length']} characters")
        print(f"API response: {result['api_response']}")
        
    except Exception as e:
        print(f"Error processing data: {e}")