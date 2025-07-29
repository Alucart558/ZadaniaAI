import requests
import re

# Dane logowania
username = "tester"
password = "574e112a"
login_url = "https://xyz.ag3nts.org/"

# Krok 1: Pobierz HTML strony logowania
response = requests.get(login_url)
html_content = response.text

# Krok 2: Wyodrębnij pytanie
match = re.search(r"Question: (.*?)</p>", html_content)
if not match:
    print("Nie udało się znaleźć pytania!")
    exit(1)
question = match.group(1).strip()
print(f"Pytanie: {question}")

# Krok 3: Pobierz odpowiedź od LLM (tu przykład na 2+2)
answer = "4" if "2+2" in question else "Sample answer"
print(f"Odpowiedź: {answer}")

# Krok 4: Wyślij POST z loginem, hasłem i answer
payload = {
    "username": username,
    "password": password,
    "answer": answer
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}
post_resp = requests.post(login_url, data=payload, headers=headers)

if post_resp.status_code == 200:
    # Odczytaj adres tajnej podstrony
    secret_url = post_resp.text.strip()
    print(f"Tajna podstrona: {secret_url}")
    # Pobierz i wyświetl jej zawartość
    secret_page = requests.get(secret_url).text
    print("Zawartość tajnej strony:")
    print(secret_page)
else:
    print(f"Błąd logowania: {post_resp.status_code} - {post_resp.text}")