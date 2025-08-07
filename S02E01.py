import requests
import zipfile
import os
import json
from openai import OpenAI
from pathlib import Path

# Initialize OpenAI client
client = OpenAI(api_key="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")

def download_and_extract_zip(url: str, extract_to: str = "przesluchania") -> str:
    """Download and extract the ZIP file with audio recordings."""
    print("Pobieranie archiwum z nagraniami...")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Błąd pobierania: {response.status_code}")
        return None
    
    # Save ZIP file
    zip_path = "przesluchania.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)
    
    # Extract ZIP
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print(f"Archiwum rozpakowane do: {extract_to}")
    return extract_to

def transcribe_audio_file(file_path: str) -> str:
    """Transcribe audio file using OpenAI Whisper."""
    print(f"Transkrybuję plik: {file_path}")
    
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pl"
            )
        return transcript.text
    except Exception as e:
        print(f"Błąd transkrypcji dla {file_path}: {e}")
        return ""

def process_all_recordings(directory: str) -> dict:
    """Process all audio files in directory and create transcriptions."""
    transcriptions = {}
    
    # Find all m4a files
    audio_files = list(Path(directory).glob("*.m4a"))
    
    print(f"Znaleziono {len(audio_files)} plików audio")
    
    for audio_file in audio_files:
        file_name = audio_file.name
        transcript = transcribe_audio_file(str(audio_file))
        transcriptions[file_name] = transcript
        print(f"Transkrypcja {file_name} ukończona")
    
    return transcriptions

def analyze_transcriptions(transcriptions: dict) -> str:
    """Analyze transcriptions to find the street name where Professor Maj's institute is located."""
    
    # Combine all transcriptions
    all_transcripts = ""
    for file_name, transcript in transcriptions.items():
        all_transcripts += f"\n\n=== NAGRANIE: {file_name} ===\n{transcript}"
    
    prompt = f"""
Twoim zadaniem jest ustalenie nazwy ulicy, na której znajduje się konkretny instytut uczelni, gdzie wykłada profesor Andrzej Maj. 

WAŻNE: Szukasz nazwy ulicy, na której znajduje się INSTYTUT, a nie główna siedziba uczelni.

Poniżej znajdują się transkrypcje przesłuchań świadków. Niektóre zeznania mogą się wykluczać lub być nieprecyzyjne. Szczególnie jedno z nagrań może być chaotyczne i wprowadzać w błąd. Analizuj wszystkie informacje krytycznie.

TRANSKRYPCJE NAGRAŃ:
{all_transcripts}

Analizuj krok po kroku:
1. Przeczytaj wszystkie transkrypcje i wynotuj informacje o profesorze Andrzej Maj
2. Znajdź informacje o uczelni/instytucie gdzie pracuje
3. Wynotuj wszystkie wspomniane nazwy ulic i lokalizacje
4. Użyj swojej wiedzy o polskich uczelniach, aby zidentyfikować konkretny instytut
5. Podaj nazwę ulicy, na której znajduje się ten instytut

Odpowiedz TYLKO nazwą ulicy, bez dodatkowych słów.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś ekspertem analitycznym. Analizujesz zeznania świadków, aby ustalić lokalizację instytutu. Odpowiadasz precyzyjnie i konkretnie."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content.strip()

def main():
    api_key = "b76d036a-560e-48a2-b895-7f7fb0115cec"
    
    # Download and extract recordings
    zip_url = "https://c3ntrala.ag3nts.org/dane/przesluchania.zip"
    extract_dir = download_and_extract_zip(zip_url)
    
    if not extract_dir:
        print("Nie udało się pobrać archiwum")
        return
    
    # Process all recordings
    print("Rozpoczynam transkrypcję nagrań...")
    transcriptions = process_all_recordings(extract_dir)
    
    if not transcriptions:
        print("Nie udało się przetworzyć żadnych nagrań")
        return
    
    print(f"Przetworzono {len(transcriptions)} nagrań")
    
    # Save transcriptions for debugging
    with open("transcriptions.json", "w", encoding="utf-8") as f:
        json.dump(transcriptions, f, ensure_ascii=False, indent=2)
    
    # Analyze transcriptions
    print("Analizuję transkrypcje...")
    street_name = analyze_transcriptions(transcriptions)
    
    print(f"Znaleziona ulica: {street_name}")
    
    # Send answer to Centrala
    report_data = {
        "task": "mp3",
        "apikey": api_key,
        "answer": street_name
    }
    
    report_url = "https://c3ntrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json"}
    
    print("Wysyłam odpowiedź do Centrali...")
    response = requests.post(report_url, json=report_data, headers=headers)
    
    if response.status_code == 200:
        print("Sukces!")
        print(response.text)
    else:
        print(f"Błąd: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()