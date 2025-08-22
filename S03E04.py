import requests
import re
import unicodedata
import time

API_KEY = "b76d036a-560e-48a2-b895-7f7fb0115cec"
PEOPLE_URL = "https://c3ntrala.ag3nts.org/people"
PLACES_URL = "https://c3ntrala.ag3nts.org/places"
REPORT_URL = "https://c3ntrala.ag3nts.org/report"
NOTE_URL = "https://c3ntrala.ag3nts.org/dane/barbara.txt"

OPENAI_API_KEY = "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"

def strip_polish(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    ).upper()

def get_note():
    r = requests.get(NOTE_URL)
    r.raise_for_status()
    return r.text

def extract_names_and_cities_regex(note):
    names = set(re.findall(r'\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,}\b', note))
    cities = set(re.findall(r'\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,}\b', note))
    return names, cities

def extract_names_and_cities_llm(note):
    import openai
    import json
    import re
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Wyodrębnij z poniższej notatki wszystkie imiona osób oraz nazwy miast. "
        "Zwróć wynik jako dwa JSONowe zbiory: {'imiona': [...], 'miasta': [...]}.\n\n"
        f"{note}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0
    )
    text = response.choices[0].message.content
    print("ODPOWIEDŹ LLM:\n", text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    try:
        data = json.loads(text)
        imiona = set(data.get("imiona", []) or data.get("Imiona", []))
        miasta = set(data.get("miasta", []) or data.get("Miasta", []))
        return imiona, miasta
    except Exception as e:
        print("Błąd dekodowania JSON z LLM:", e)
        return set(), set()

def query_people(name):
    payload = {"apikey": API_KEY, "query": strip_polish(name)}
    print(f"Zapytanie do PEOPLE: {payload}")
    r = requests.post(PEOPLE_URL, json=payload)
    print(f"Odpowiedź PEOPLE: {r.status_code} {r.text}")
    r.raise_for_status()
    try:
        data = r.json()
        # Jeśli message zawiera dane, rozdziel po spacjach
        msg = data.get("message", "")
        if msg and "[**RESTRICTED DATA**]" not in msg:
            return msg.strip().split()
        return []
    except Exception:
        return []

def query_places(city):
    payload = {"apikey": API_KEY, "query": strip_polish(city)}
    print(f"Zapytanie do PLACES: {payload}")
    r = requests.post(PLACES_URL, json=payload)
    print(f"Odpowiedź PLACES: {r.status_code} {r.text}")
    r.raise_for_status()
    try:
        data = r.json()
        msg = data.get("message", "")
        if msg and "[**RESTRICTED DATA**]" not in msg:
            return msg.strip().split()
        return []
    except Exception:
        return []

def send_answer(city):
    payload = {
        "task": "loop",
        "apikey": API_KEY,
        "answer": city
    }
    r = requests.post(REPORT_URL, json=payload)
    print("CENTRALA:", r.status_code, r.text)
    return r.status_code, r.text

def main():
    note = get_note()
    print("NOTATKA:\n", note)

    names, cities = set(), set()
    if OPENAI_API_KEY:
        names, cities = extract_names_and_cities_llm(note)
    if not names and not cities:
        names, cities = extract_names_and_cities_regex(note)

    print("Imiona z notatki:", names)
    print("Miasta z notatki:", cities)

    checked_names = set()
    checked_cities = set()
    kolejka_osob = set(strip_polish(n) for n in names)
    kolejka_miast = set(strip_polish(c) for c in cities)
    miejsca_barbary = set()
    znalezione_miasto = None

    # Zbierz wszystkie znane miasta z notatki i z odpowiedzi PEOPLE
    znane_miasta = set(strip_polish(c) for c in cities)
    miejsca_osob = set()

    if "BARBARA" in kolejka_osob:
        miejsca_barbary.update(query_people("BARBARA"))

    while kolejka_osob or kolejka_miast:
        while kolejka_osob:
            name = kolejka_osob.pop()
            if name in checked_names:
                continue
            checked_names.add(name)
            print(f"Sprawdzam osobę: {name}")
            try:
                miejsca = query_people(name)
            except Exception as e:
                print(f"Błąd dla osoby {name}: {e}")
                continue
            print(f"Miejsca dla {name}:", miejsca)
            for m in miejsca:
                m_norm = strip_polish(m)
                miejsca_osob.add(m_norm)
                if m_norm not in checked_cities:
                    kolejka_miast.add(m_norm)
            if name == "BARBARA":
                miejsca_barbary.update(miejsca)
            time.sleep(0.5)

            while kolejka_miast:
                city = kolejka_miast.pop()
                if city in checked_cities:
                    continue
                checked_cities.add(city)
                print(f"Sprawdzam miasto: {city}")
                try:
                    osoby = query_places(city)
                except Exception as e:
                    print(f"Błąd dla miasta {city}: {e}")
                    continue
                print(f"Osoby w {city}:", osoby)
                for o in osoby:
                    o_norm = strip_polish(o)
                    if o_norm not in checked_names:
                        kolejka_osob.add(o_norm)
                # Szukaj Barbary tylko w nowych miastach!
                if "BARBARA" in [strip_polish(x) for x in osoby]:
                    if city not in znane_miasta:
                        znalezione_miasto = city
                        print("Znaleziono nowe miejsce Barbary:", city)
                        break
                time.sleep(0.5)
        if znalezione_miasto:
            break

    if znalezione_miasto:
        send_answer(znalezione_miasto)
    else:
        print("Nie znaleziono nowego miasta Barbary.")

if __name__ == "__main__":
    main()