import requests
import json
import base64
from openai import OpenAI
import re

# Initialize OpenAI client
client = OpenAI(api_key="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")

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_map_fragments():
    """Analyze map fragments to identify the city"""
    
    # Encode all map images
    map_images = []
    for i in range(1, 5):
        image_path = f"C:/Users/dawib/Downloads/mapa{i}.png"
        try:
            encoded_image = encode_image(image_path)
            map_images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{encoded_image}"
                }
            })
            print(f"Successfully loaded mapa{i}.png")
        except FileNotFoundError:
            print(f"Warning: mapa{i}.png not found")
    
    if not map_images:
        print("No map images found!")
        return None
    
    # Try completely different approach - maybe it's not a typical city
    messages = [
        {
            "role": "system",
            "content": """Jesteś ekspertem kartografem. 

ZADANIE: Przeanalizuj fragmenty mapy i zidentyfikuj miasto.

MOŻLIWE SCENARIUSZE:
1. To może być bardzo małe miasto/miasteczko
2. To może być dzielnica większego miasta
3. To może być miejscowość turystyczna/uzdrowiskowa
4. To może być miasto przemysłowe
5. To może być miasto z nietypowym układem ulic

INSTRUKCJA:
- Przeczytaj WSZYSTKIE nazwy ulic z każdego fragmentu
- Znajdź charakterystyczne nazwy (np. ul. Dworcka = blisko dworca)
- Zwróć uwagę na typ zabudowy (bloki, domki, przemysł)
- Jeden fragment może być z innego miasta - zignoruj go

ODPOWIEDŹ: Podaj nazwę miasta lub miejscowości w Polsce."""
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Przeanalizuj te fragmenty mapy i podaj nazwę polskiego miasta lub miejscowości. Może to być małe miasto lub dzielnica."
                }
            ] + map_images
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=100,
            temperature=0.3
        )
        
        full_response = response.choices[0].message.content.strip()
        print(f"Pełna odpowiedź: {full_response}")
        
        # Better extraction of city name from response
        city_name = None
        
        # Check for specific cities mentioned in bold or explicitly
        if "**Ostróda**" in full_response or "Ostróda" in full_response:
            city_name = "Ostróda"
        elif "**Pabianice**" in full_response or "Pabianice" in full_response:
            city_name = "Pabianice"
        else:
            # Try to extract any location name
            # Look for Polish location patterns
            location_patterns = [
                r'\*\*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+)*)\*\*',  # Bold text
                r'to\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+)*)',
                r'miasta?\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+)*)',
                r'\b([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+)*)\b'
            ]
            
            for pattern in location_patterns:
                matches = re.findall(pattern, full_response)
                if matches:
                    potential_location = matches[0].strip()
                    # Clean up common words
                    if potential_location.lower() not in ['to', 'jest', 'może', 'być', 'miasto', 'fragment', 'ulica', 'nazwa', 'podstawie', 'analizy', 'nazw', 'można', 'stwierdzić']:
                        city_name = potential_location
                        break
        
        if city_name:
            print(f"Rozpoznane miasto: {city_name}")
            return city_name
        
        return None
        
    except Exception as e:
        print(f"Błąd API: {e}")
        return None

def submit_answer(city_name):
    """Submit the answer to Centrala"""
    api_key = "b76d036a-560e-48a2-b895-7f7fb0115cec"
    
    report_data = {
        "task": "mp3",
        "apikey": api_key,
        "answer": city_name
    }
    
    report_url = "https://c3ntrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json"}
    
    print(f"Wysyłam odpowiedź: {city_name}")
    response = requests.post(report_url, json=report_data, headers=headers)
    
    if response.status_code == 200:
        print("Sukces!")
        print(response.text)
        return True
    else:
        print(f"Błąd: {response.status_code}")
        print(response.text)
        return False

def main():
    print("Rozpoczynam analizę fragmentów mapy...")
    
    # Analyze map fragments
    city_name = analyze_map_fragments()
    
    if city_name:
        # Submit the answer
        submit_answer(city_name)
    else:
        print("Nie udało się rozpoznać miasta")

if __name__ == "__main__":
    main()