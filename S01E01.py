import os
import requests
import re
from openai import OpenAI

client = OpenAI(api_key="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")

def get_llm_answer(q: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś asystentem matematyczno-logicznym. Odpowiadaj TYLKO LICZBĄ bez żadnych dodatkowych słów, jednostek czy oznaczeń."},
            {"role": "user",   "content": q}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()

def main():
    username = "tester"
    password = "574e112a"
    login_url = "https://xyz.ag3nts.org/"

    # 1) pobierz stronę
    r = requests.get(login_url)
    html = r.text
    
    # 2) wyciągnij pytanie - poprawiony regex dla struktury z <br />
    patterns = [
        r'<p id="human-question">Question:<br\s*/>(.*?)</p>',  # główny wzorzec
        r'>Question:<br\s*/>\s*(.*?)<',                        # alternatywny
        r'Question:<br\s*/>\s*(.*?)(?:</p>|<)',               # kolejny
        r'>Question:\s*(.*?)<'                                 # oryginalny
    ]
    
    question = None
    for pattern in patterns:
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            question = m.group(1).strip()
            print(f"Znaleziono pytanie wzorcem '{pattern}': {question}")
            break
    
    if not question:
        print("Nie udało się znaleźć pytania!")
        return
    
    print("Pytanie:", question)

    # 3) lecimy do LLM
    answer = get_llm_answer(question)
    print("Odpowiedź:", answer)

    # 4) wyślij POST
    data = {"username": username, "password": password, "answer": answer}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    post = requests.post(login_url, data=data, headers=headers)

    if post.status_code != 200:
        print("Błąd logowania:", post.status_code)
        print(post.text)
        return

    result = post.text.strip()
    if "{{FLG:" in result:
        print("Znaleziono flagę na stronie!")
        
        # Sprawdź czy jest link do pliku firmware
        firmware_match = re.search(r'href="(/files/[^"]+)"', result)
        if firmware_match:
            firmware_url = "https://xyz.ag3nts.org" + firmware_match.group(1)
            print(f"Pobieranie firmware z: {firmware_url}")
            
            firmware_resp = requests.get(firmware_url)
            if firmware_resp.status_code == 200:
                print("Zawartość pliku firmware:")
                print(firmware_resp.text)
            else:
                print(f"Błąd pobierania firmware: {firmware_resp.status_code}")
        
        print("Pełna zawartość strony:")
        print(result)
    elif result.startswith("http"):
        secret_page = requests.get(result).text
        print("Zawartość tajnej strony:")
        print(secret_page)
    else:
        print("Logowanie nie powiodło się, serwer zwrócił:")
        print(result)

if __name__ == "__main__":
    main()