import requests
import zipfile
import os
import json
import uuid
import time
import re
from datetime import datetime
from openai import OpenAI

API_KEY = "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"
EMBEDDING_MODEL = "text-embedding-ada-002"
VECTOR_DB_URL = "http://localhost:6333"
COLLECTION_NAME = "reports"
VECTOR_SIZE = 1536

# Usuń starą kolekcję, jeśli istnieje
requests.delete(f"{VECTOR_DB_URL}/collections/{COLLECTION_NAME}")

def create_collection():
    url = f"{VECTOR_DB_URL}/collections/{COLLECTION_NAME}"
    payload = {
        "vectors": {
            "size": VECTOR_SIZE,
            "distance": "Cosine"
        }
    }
    r = requests.put(url, json=payload)
    if r.status_code == 200:
        print("Create collection: OK")
    elif r.status_code == 409:
        print("Create collection: already exists")
    else:
        print("Create collection:", r.status_code, r.text)

create_collection()

def download_file(url, destination):
    response = requests.get(url)
    response.raise_for_status()
    with open(destination, 'wb') as file:
        file.write(response.content)
    return destination

def extract_zip(zip_path, extract_to, password=None):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        if password:
            zip_ref.extractall(extract_to, pwd=bytes(password, 'utf-8'))
        else:
            zip_ref.extractall(extract_to)
    return extract_to

def generate_embedding(text, model=EMBEDDING_MODEL):
    client = OpenAI(api_key=API_KEY)
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding

def send_answer_to_central(answer_date):
    url = "https://c3ntrala.ag3nts.org/report"
    payload = {
        "task": "wektory",
        "apikey": "b76d036a-560e-48a2-b895-7f7fb0115cec",
        "answer": answer_date
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print("CENTRALA:", response.status_code, response.text)
    return response.status_code, response.text

def save_embedding_to_vector_db(embedding, report_date):
    point_id = str(uuid.uuid4())
    payload = {
        "points": [{
            "id": point_id,
            "vector": embedding,
            "payload": {"date": report_date}
        }]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.put(
        f"{VECTOR_DB_URL}/collections/{COLLECTION_NAME}/points?wait=true",
        json=payload,
        headers=headers
    )
    if response.status_code == 200:
        print(f"[Qdrant] Dodano punkt: {point_id} | data: {report_date}")
    else:
        print(f"[Qdrant] Błąd zapisu: {response.status_code} {response.text}")

def query_vector_database(question):
    question_embedding = generate_embedding(question, model=EMBEDDING_MODEL)
    response = requests.post(
        f"{VECTOR_DB_URL}/collections/{COLLECTION_NAME}/points/search",
        json={
            "vector": question_embedding,
            "limit": 1,
            "with_payload": True
        }
    )
    if response.status_code == 200:
        results = response.json()
        if results.get('result'):
            top = results['result'][0]
            payload = top.get('payload', {})
            date = payload.get('date')
            print(f"[Qdrant] Najlepszy wynik: id={top.get('id')} | score={top.get('score'):.3f} | data={date}")
            return date
        else:
            print("[Qdrant] Brak wyników.")
    else:
        print(f"[Qdrant] Błąd zapytania: {response.status_code} {response.text}")
    return None

def main():
    # 1. Pobierz i rozpakuj główne archiwum
    zip_url = "https://c3ntrala.ag3nts.org/dane/pliki_z_fabryki.zip"
    main_zip = download_file(zip_url, "pliki_z_fabryki.zip")
    extract_zip(main_zip, "pliki_z_fabryki")

    # 2. Rozpakuj weapons_tests.zip z hasłem
    weapons_zip_path = os.path.join("pliki_z_fabryki", "weapons_tests.zip")
    extract_zip(weapons_zip_path, "weapons_tests", password="1670")

    # 3. Przetwórz każdy raport
    reports_dir = os.path.join("weapons_tests", "do-not-share")
    for report_file in os.listdir(reports_dir):
        if report_file.endswith(".txt"):
            report_path = os.path.join(reports_dir, report_file)
            # Wyciągnij datę w formacie YYYY_MM_DD z nazwy pliku
            m = re.match(r"(\d{4}_\d{2}_\d{2})", report_file)
            if m:
                report_date = m.group(1).replace("_", "-")  # Zamień na standardowy format daty
            else:
                print(f"Nie udało się wyciągnąć daty z pliku: {report_file}")
                continue
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            embedding = generate_embedding(content, model=EMBEDDING_MODEL)
            save_embedding_to_vector_db(embedding, report_date)
            time.sleep(1)   # Możesz skrócić lub usunąć, jeśli masz mało plików

    # 4. Zapytaj bazę o datę kradzieży prototypu
    question = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
    theft_date = query_vector_database(question)

    # 5. Wyślij odpowiedź do centrali
    if theft_date:
        send_answer_to_central(theft_date)
    else:
        print("Nie znaleziono odpowiedzi.")

if __name__ == "__main__":
    main()