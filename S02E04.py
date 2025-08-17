import os
import json
import requests

# Jeśli chcesz użyć OCR i transkrypcji, zainstaluj:
# pip install pytesseract pillow openai

import pytesseract
from PIL import Image
import openai

# Ustaw swój klucz API OpenAI jeśli używasz whisper/gpt-4o
OPENAI_API_KEY = "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"

def extract_text_from_txt(filepath):
    with open(filepath, encoding="utf-8") as f:
        return f.read()

def extract_text_from_png(filepath):
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang="eng+pol")
        return text
    except Exception as e:
        print(f"OCR error for {filepath}: {e}")
        return ""

def extract_text_from_mp3(filepath):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        with open(filepath, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"Transcription error for {filepath}: {e}")
        return ""

def categorize_with_gpt(text):
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Przeczytaj poniższą notatkę z fabryki i zdecyduj, czy dotyczy:\n"
        "- schwytanych ludzi lub jednoznacznych śladów ich obecności (odpowiedz: people)\n"
        "- naprawy usterki sprzętowej (hardware, czyli fizycznych elementów, np. antena, czujnik, ogniwo, przewód, panel, sensor, przekaźnik; odpowiedz: hardware)\n"
        "- żadnej z powyższych (odpowiedz: none)\n\n"
        "UWAGA: Jeśli w raporcie jest napisane, że nikogo nie znaleziono, nie klasyfikuj jako people.\n"
        "UWAGA: Jeśli w raporcie są tylko żarty, prośby, rozmowy o jedzeniu, pizza, nastrojach, prośby o dostawę lub inne tematy niezwiązane z obecnością ludzi, NIE klasyfikuj jako people.\n"
        "UWAGA: Klasyfikuj jako people TYLKO jeśli jest wyraźnie mowa o schwytaniu człowieka, przekazaniu do kontroli, analizie biometrycznej, odciskach palców, znalezieniu osoby lub śladów jej obecności.\n"
        "UWAGA: NIE klasyfikuj jako hardware żadnych raportów dotyczących aktualizacji, konfiguracji, testów, zmian w oprogramowaniu, protokołach, szyfrowaniu, kanałach komunikacyjnych, systemach, algorytmach, AI, software, itp.\n"
        "Hardware to wyłącznie naprawa, wymiana lub usunięcie usterki fizycznego elementu urządzenia.\n"
        f"NOTATKA:\n{text}\n\n"
        "Odpowiedz tylko jednym słowem: people, hardware lub none."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś asystentem do klasyfikacji raportów fabrycznych."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        answer = resp.choices[0].message.content.strip().lower()
        if answer == "people":
            return "people"
        if answer == "hardware":
            return "hardware"
        return None
    except Exception as e:
        print(f"AI error: {e}")
        return None

def main():
    folder = r"C:\Users\dawib\Downloads\pliki_z_fabryki"
    answer = {"people": [], "hardware": []}

    for root, dirs, files in os.walk(folder):
        # Pomijaj folder "facts"
        if "facts" in root:
            continue
        for filename in files:
            if filename == "weapons_tests.zip" or "." not in filename:
                continue
            ext = filename.lower().split(".")[-1]
            filepath = os.path.join(root, filename)
            text = ""
            if ext == "txt":
                text = extract_text_from_txt(filepath)
            elif ext == "png":
                text = extract_text_from_png(filepath)
            elif ext == "mp3":
                text = extract_text_from_mp3(filepath)
            else:
                continue
            print(f"\n==== {filename} ====\n{text}\n====================\n")  # <-- dodaj to
            cat = categorize_with_gpt(text)
            if cat:
                answer[cat].append(filename)

    # Sortuj alfabetycznie
    answer["people"].sort()
    answer["hardware"].sort()

    payload = {
        "task": "kategorie",
        "apikey": "b76d036a-560e-48a2-b895-7f7fb0115cec",
        "answer": answer
    }

    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Wysyłka do centrali
    url = "https://c3ntrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers)
    print("Status:", resp.status_code)
    print("Odpowiedź:", resp.text)

if __name__ == "__main__":
    main()