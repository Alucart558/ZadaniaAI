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

def systematic_analysis():
    """Systematic step-by-step analysis"""
    
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
    
    # POJEDYNCZY SKUTECZNY PROMPT
    final_question = """Przeanalizuj te 4 mapy polskiego miasta:

Otrzymujesz kilka fragmentów mapy, a twoim zadaniem jest precyzyjne określenie, z jakiego miasta pochodzi każdy z nich. Jeden z fragmentów jest błędny i przedstawia inne miasto niż pozostałe. Dla każdego fragmentu ustal prawidłowe miasto, a dla błędnego fragmentu wskaż zarówno miasto, które faktycznie przedstawia, jak i miasto, z którym został błędnie powiązany.
Dla każdego fragmentu mapy wykonaj następujące kroki:

Identyfikacja ulic: Dokładnie wypisz nazwy wszystkich widocznych ulic na fragmencie mapy. Jeśli nazwy ulic są częściowo widoczne lub nieczytelne, zanotuj wszelkie czytelne fragmenty i użyj ich jako wskazówek.
1.Rozpoznanie punktów charakterystycznych: Zidentyfikuj i opisz wszelkie znaczące punkty orientacyjne, takie jak cmentarze, kościoły, szkoły, szpitale, parki, rzeki, mosty lub inne istotne obiekty. Podaj szczegółowe informacje (np. nazwy budynków lub rodzaj punktów orientacyjnych), jeśli są widoczne.
2.Analiza układu urbanistycznego: Przeanalizuj układ urbanistyczny, w tym schemat ulic (np. siatka, układ promienisty, nieregularny), obecność elementów naturalnych (np. rzeki, jeziora) oraz gęstość lub rozmieszczenie budynków. Zwróć uwagę na charakterystyczne cechy, takie jak ronda, główne skrzyżowania lub unikalne kształty dróg.
3.Weryfikacja: Zweryfikuj zidentyfikowane ulice, punkty orientacyjne i układ urbanistyczny, korzystając z wiarygodnych źródeł (np. internetowych baz danych map, danych geograficznych lub wyszukiwania w internecie), aby potwierdzić, że są zgodne z proponowanym miastem. Upewnij się, że wszystkie elementy pasują do geografii i infrastruktury wskazanego miasta.
4.Wykrywanie błędu: Dla błędnego fragmentu wyjaśnij, dlaczego nie pasuje do tego samego miasta co pozostałe. Podaj dowody (np. niezgodne nazwy ulic, punkty orientacyjne lub układ urbanistyczny) i określ, jakie miasto faktycznie przedstawia.

Jeśli jakiekolwiek szczegóły mapy są niejasne (np. rozmazany tekst lub nieczytelne punkty orientacyjne) sformułuj uzasadnioną hipotezę na podstawie najbardziej prawdopodobnej interpretacji widocznych elementów. W razie potrzeby skorzystaj z zewnętrznych źródeł, aby zweryfikować swoje ustalenia, ale priorytetowo traktuj dowody bezpośrednio pochodzące z fragmentów mapy. Upewnij się, że odpowiedź jest precyzyjna i unika założeń nieprzynoszących się do danych widocznych na mapie.
UWAGA: PODAJ TYLKO JEDNĄ NAZWĘ MIASTA! Nie pisz "może być" ani "prawdopodobnie".

ZAKOŃCZ ODPOWIEDŹ W FORMACIE:
MIASTO: [nazwa miasta]"""

    messages = [
        {
            "role": "system", 
            "content": """Jesteś ekspertem polskich miast i topografii. 

MUSISZ podać konkretną nazwę miasta na podstawie analizy map.
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
        print("ANALIZA WSZYSTKICH FRAGMENTÓW JEDNOCZEŚNIE")
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
    """Extract city name from analysis"""
    
    # Szukaj wzorców - dodaj więcej opcji
    patterns = [
        r'MIASTO:\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s-]+)',
        r'miasto to\s*:?\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s-]+)',
        r'(?:^|\n)\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{4,})\s*(?:\.|$)',
        r'reprezentuje\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s-]+)',
        r'to\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{4,})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis_text, re.MULTILINE)
        if match:
            city = match.group(1).strip('.,!?:() ')
            # Filtruj niepożądane słowa
            if (len(city) >= 3 and 
                city.lower() not in ['nieznane', 'potrzebuję', 'więcej', 'danych', 'miasto', 'fragment', 'jest', 'może']):
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
    print("🗺️ === AUTOMATYCZNA ANALIZA MAP === 🗺️")
    
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