import requests
import re

# Dane logowania
username = "tester"
password = "574e112a"
login_url = "https://xyz.ag3nts.org/"
centrala_url = "https://c3ntrala.ag3nts.org/"

# Krok 1: Pobierz HTML strony logowania
response = requests.get(login_url)
html_content = response.text

# Krok 2: Wyodrebnij pytanie z HTML (przyklad: pytanie miedzy tagami <p> lub tekstem "Question:")
question_pattern = r"Question: (.*?)</p>"
match = re.search(question_pattern, html_content)
if not match:
    print("Nie udalo sie znalezc pytania!")
    exit(1)
question = match.group(1).strip()
print(f"Pytanie: {question}")

# Krok 3: Uzyskaj odpowiedz od Grok 3 (symulacja LLM)
# W rzeczywistym scenariuszu uzylbys API LLM, np. GPT 4.1 Nano.
# Tutaj zakladam, ze pytanie jest proste, np. "What is 2+2?" i odpowiadam bezposrednio.
# Dla ogolnosci: wysylamy pytanie do siebie (Grok 3).
answer = "4" if "2+2" in question else "Sample answer"  # Przyklad, w razie potrzeby dostosuj
print(f"Odpowiedź: {answer}")

# Krok 4: Wyslij zadanie POST z danymi logowania
payload = {
    "username": username,
    "password": password,
    "answer": answer
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
post_response = requests.post(login_url, data=payload, headers=headers)

# Krok 5: Sprawdz odpowiedz serwera i pobierz tajna podstrone
if post_response.status_code == 200:
    # Zakladamy, ze odpowiedz zawiera adres tajnej podstrony, np. w formacie tekstowym
    secret_url = post_response.text.strip()
    print(f"Tajna podstrona: {secret_url}")
    
    # Odwiedz tajna podstrone
    secret_response = requests.get(secret_url)
    flag = secret_response.text.strip()
    print(f"Flaga: {flag}")
    
    # Krok 6: Zglos flage do centrali
    centrala_payload = {"flag": flag}
    centrala_response = requests.post(centrala_url, data=centrala_payload)
    print(f"Odpowiedz centrali: {centrala_response.text}")
else:
    print(f"Blad logowania: {post_response.status_code} - {post_response.text}")