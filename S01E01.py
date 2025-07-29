import os
import requests
import re
from openai import OpenAI

client = OpenAI(api_key="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")

def get_llm_answer(q: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś asystentem matematyczno-logicznym."},
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

    # 2) wyciągnij pytanie
    m = re.search(r">Question:\s*(.*?)<", html, re.DOTALL)
    if not m:
        print("Nie udało się znaleźć pytania!")
        return
    question = m.group(1).strip()
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
    if result.startswith("http"):
        secret_page = requests.get(result).text
        print("Zawartość tajnej strony:")
        print(secret_page)
    else:
        # np. „Anty-human captcha incorrect!”
        print("Logowanie nie powiodło się, serwer zwrócił:")
        print(result)

if __name__ == "__main__":
    main()