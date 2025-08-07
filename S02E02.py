import requests
import base64
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key="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")

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_map_file():
    """Load the map file from downloads directory."""
    downloads_path = os.path.expanduser("~/Downloads")
    map_path = os.path.join(downloads_path, "mapa.png")
    
    if os.path.exists(map_path):
        print(f"Found map file: {map_path}")
        return map_path
    else:
        # Try current directory as fallback
        current_map_path = "mapa.png"
        if os.path.exists(current_map_path):
            print(f"Found map file in current directory: {current_map_path}")
            return current_map_path
        else:
            print(f"Map file not found in: {map_path}")
            print(f"Also tried current directory: {current_map_path}")
            return None

def analyze_map(map_file):
    """Analyze map using GPT-4o Vision."""
    
    # Prepare image for the API
    base64_image = encode_image(map_file)
    image = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{base64_image}"
        }
    }
    
    # Prepare the prompt
    prompt = """Analizujesz mapę polskiego miasta. Twoim zadaniem jest określenie, z jakiego miasta pochodzi ta mapa.

WAŻNE INFORMACJE:
- Mapa może zawierać fragmenty z różnych części miasta
- Niektóre fragmenty mogą być błędne i pochodzić z innego miasta
- Skupij się na nazwach ulic, charakterystycznych obiektach (cmentarze, kościoły, szkoły, parki)
- Zwróć uwagę na układ urbanistyczny i topografię
- Upewnij się, że lokacje które rozpoznajesz rzeczywiście znajdują się w mieście, które chcesz wskazać

INSTRUKCJE:
1. Przeanalizuj wszystkie widoczne fragmenty mapy
2. Zidentyfikuj nazwy ulic i charakterystyczne obiekty
3. Określ które fragmenty pasują do siebie geograficznie
4. Zidentyfikuj fragmenty które mogą być błędne (jeśli takie istnieją)
5. Na podstawie spójnych fragmentów określ nazwę miasta

Odpowiedz TYLKO nazwą miasta, bez dodatkowych oznaczeń."""

    # Create message with image
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                image
            ]
        }
    ]
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        max_tokens=1000,
        temperature=0
    )
    
    return response.choices[0].message.content.strip()

def submit_answer(city_name):
    """Submit the answer to Centrala."""
    api_key = "b76d036a-560e-48a2-b895-7f7fb0115cec"
    
    report_data = {
        "task": "maps",
        "apikey": api_key,
        "answer": city_name
    }
    
    report_url = "https://c3ntrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json"}
    
    print(f"Submitting answer: {city_name}")
    response = requests.post(report_url, json=report_data, headers=headers)
    
    if response.status_code == 200:
        print("Success!")
        print(response.text)
        return True
    else:
        print(f"Error submitting answer: {response.status_code}")
        print(response.text)
        return False

def main():
    print("Starting map analysis task...")
    
    # Step 1: Load map file
    print("Step 1: Loading map file...")
    map_file = load_map_file()
    
    if not map_file:
        print("Error: Could not find map file 'mapa.png' in Downloads folder or current directory")
        return
    
    # Step 2: Analyze map with Vision model
    print("Step 2: Analyzing map with GPT-4o Vision...")
    city_name = analyze_map(map_file)
    
    print(f"Identified city: {city_name}")
    
    # Step 3: Submit answer
    print("Step 3: Submitting answer...")
    success = submit_answer(city_name)
    
    if success:
        print("Task completed successfully!")
    else:
        print("Task failed. You may need to try again with a different approach.")

if __name__ == "__main__":
    main()