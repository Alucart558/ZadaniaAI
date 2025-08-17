import requests
import json
import base64
from openai import OpenAI
import re
import pytesseract
from PIL import Image

# Jeśli Tesseract nie jest w PATH, odkomentuj i ustaw ścieżkę:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize OpenAI client
client = OpenAI(api_key="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")

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='pol')
        # Usuwamy nadmiarowe białe znaki
        return text.strip()
    except Exception as e:
        print(f"OCR error for {image_path}: {e}")
        return ""

def systematic_analysis():
    """Systematic step-by-step analysis with OCR"""
    map_images = []
    ocr_texts = []
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
            ocr_text = extract_text_from_image(image_path)
            ocr_texts.append(ocr_text)
            print(f"Successfully loaded mapa{i}.png, OCR: {ocr_text[:60]}...")
        except FileNotFoundError:
            print(f"Warning: mapa{i}.png not found")
            ocr_texts.append("")

    # Budujemy prompt z tekstem OCR
    ocr_prompt = ""
    for idx, text in enumerate(ocr_texts, 1):
        ocr_prompt += f"\nFragment {idx} - tekst z mapy (OCR):\n{text if text else '[brak tekstu]'}\n"

    final_question = f"""Przeanalizuj te 4 mapy polskiego miasta.

Najpierw przeanalizuj tekst wyciągnięty z mapy (OCR) dla każdego fragmentu, potem porównaj z obrazem.
Dla każdego fragmentu:
- Wypisz nazwy ulic i punkty charakterystyczne na podstawie OCR i obrazu.
- Sprawdź, w jakim mieście występuje taki układ ulic i obiektów.
- Jeśli fragment pochodzi z innego miasta, wskaż to.

{ocr_prompt}

Na końcu odpowiedzi napisz osobną linię:
MIASTO: [nazwa miasta]
Nie dodawaj żadnych innych słów po tej linii.
"""

    messages = [
        {
            "role": "system",
            "content": """Jesteś ekspertem polskich miast i topografii.

MUSISZ podać konkretną nazwę miasta na podstawie analizy map i tekstu z OCR.
NIE pisz "potrzebuję więcej danych" - przeanalizuj dokładnie i podaj najlepszy wybór."""
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": final_question
                }
            ] + map_images
        }
    ]

    try:
        print("\n" + "="*80)
        print("ANALIZA WSZYSTKICH FRAGMENTÓW JEDNOCZEŚNIE (Z OCR)")
        print("="*80)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1500,
            temperature=0.0
        )

        answer = response.choices[0].message.content.strip()
        print(f"ODPOWIEDŹ:\n{answer}")

        return answer

    except Exception as e:
        print(f"Błąd API: {e}")
        return None

def extract_city_name(analysis_text):
    """Extract city name from analysis (szuka tylko linii MIASTO:)"""
    match = re.search(r'^MIASTO:\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s-]+)$', analysis_text, re.MULTILINE)
    if match:
        city = match.group(1).strip()
        if len(city) >= 3 and city.lower() not in ['nieznane', 'potrzebuję', 'więcej', 'danych', 'miasto', 'fragment', 'jest', 'może']:
            return city
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

    print(f"\n🚀 Wysyłam odpowiedź: {city_name}")
    response = requests.post(report_url, json=report_data, headers=headers)

    if response.status_code == 200:
        print("✅ SUKCES!")
        print(response.text)
        return True
    else:
        print(f"❌ Błąd: {response.status_code}")
        print(response.text)
        return False

def main():
    print("🗺️ === AUTOMATYCZNA ANALIZA MAP (Z OCR) === 🗺️")

    # Uruchom analizę
    analysis = systematic_analysis()

    if analysis:
        # Wyciągnij nazwę miasta
        city = extract_city_name(analysis)

        if city:
            print(f"\n🎯 ZIDENTYFIKOWANE MIASTO: {city}")
            # Automatycznie wyślij
            submit_answer(city)
        else:
            print(f"\n❓ Nie udało się automatycznie wyciągnąć miasta z odpowiedzi:")
            print(analysis[-200:])  # Ostatnie 200 znaków
    else:
        print("❌ Błąd podczas analizy")

if __name__ == "__main__":
    main()