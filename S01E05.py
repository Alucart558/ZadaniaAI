import requests
import re
import json
from openai import OpenAI
from typing import Dict, Any

# Initialize OpenAI client
client = OpenAI(api_key="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")

def download_data(url: str) -> str:
    """Download data from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise Exception(f"Failed to download data: {e}")

def censor_with_llm(text: str) -> str:
    """Use LLM to censor personal information according to specific rules."""
    prompt = f"""Ocenzuruj następujący tekst zgodnie z zasadami:
1. Zamień imię i nazwisko (razem) na słowo "CENZURA"
2. Zamień wiek na słowo "CENZURA" 
3. Zamień miasto na słowo "CENZURA"
4. Zamień ulicę z numerem domu (razem) na "ul. CENZURA"

WAŻNE: Zachowaj oryginalny format tekstu (kropki, przecinki, spacje). Nie zmieniaj niczego poza danymi osobowymi.

Tekst do ocenzurowania:
{text}

Zwróć tylko ocenzurowany tekst bez dodatkowych komentarzy."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś systemem cenzury danych osobowych. Cenzurujesz tylko wskazane dane osobowe, zachowując resztę tekstu bez zmian."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def send_to_api(censored_data: str, task_name: str = "CENZURA", api_key: str = None) -> Dict[str, Any]:
    """Send censored data to the API."""
    payload = {
        "task": task_name,
        "apikey": api_key,
        "answer": censored_data
    }
    
    try:
        response = requests.post("https://c3ntrala.ag3nts.org/report", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to send data to API: {e}")

def main():
    # Correct API key from S01E03.py
    api_key = "b76d036a-560e-48a2-b895-7f7fb0115cec"
    
    # Properly formatted URL
    data_url = f"https://c3ntrala.ag3nts.org/data/{api_key}/cenzura.txt"
    
    print(f"Downloading data from: {data_url}")
    
    try:
        # Download data
        raw_data = download_data(data_url)
        print(f"Downloaded data: {raw_data}")
        
        # Censor personal information using LLM
        print("Censoring data...")
        censored_data = censor_with_llm(raw_data)
        print(f"Censored data: {censored_data}")
        
        # Send to API
        print("Sending to API...")
        result = send_to_api(censored_data, "CENZURA", api_key)
        
        print("Data processing completed successfully!")
        print(f"API response: {result}")
        
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()