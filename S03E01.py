import os
import json
import re
import requests
from openai import OpenAI

API_KEY = "b76d036a-560e-48a2-b895-7f7fb0115cec"
OPENAI_API_KEY = "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"
REPORTS_DIR = r"C:\Users\dawib\Downloads\pliki_z_fabryki"
FACTS_DIR = os.path.join(REPORTS_DIR, "facts")
NUM_REPORTS = 10

client = OpenAI(api_key=OPENAI_API_KEY)

def load_facts(facts_dir):
    facts = []
    for fname in os.listdir(facts_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(facts_dir, fname), encoding="utf-8") as f:
                facts.append(f.read())
    return facts

def extract_names(text):
    return set(re.findall(r"\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+ [A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+\b", text))

def generate_keywords_ai(report_text, facts_texts, report_file):
    prompt = f"""
Twoje zadanie: wygeneruj listę słów kluczowych w mianowniku, po polsku, oddzielonych przecinkami, które najlepiej opisują poniższy raport bezpieczeństwa. Uwzględnij osoby, miejsca, zdarzenia, technologie, powiązania z faktami i nazwą pliku. Słowa kluczowe mają być konkretne i zgodne z treścią raportu oraz powiązanych faktów. Nie powtarzaj słów, nie używaj odmian.

NAZWA PLIKU: {report_file}

RAPORT:
{report_text}

POWIĄZANE FAKTY:
{" ".join(facts_texts)}

Odpowiedz tylko jako lista słów kluczowych, bez dodatkowych komentarzy.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def main():
    # Wczytaj fakty
    facts_texts = load_facts(FACTS_DIR)
    facts_by_person = {}
    for fact in facts_texts:
        for name in extract_names(fact):
            facts_by_person.setdefault(name, []).append(fact)

    # Wczytaj raporty
    report_files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(".txt")])[:NUM_REPORTS]
    answer = {}

    for report_file in report_files:
        with open(os.path.join(REPORTS_DIR, report_file), encoding="utf-8") as f:
            report_text = f.read()
        # Znajdź osoby z raportu i powiązane fakty
        persons = extract_names(report_text)
        related_facts = []
        for person in persons:
            related_facts.extend(facts_by_person.get(person, []))
        # Generuj słowa kluczowe AI
        keywords = generate_keywords_ai(report_text, related_facts, report_file)
        answer[report_file] = keywords

    payload = {
        "task": "dokumenty",
        "apikey": API_KEY,
        "answer": answer
    }

    # Wyślij do API
    url = "https://c3ntrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers)
    print("Status:", resp.status_code)
    print("Odpowiedź:", resp.text)

if __name__ == "__main__":
    main()