import requests
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")

# Fałszywe informacje z pamięci robota
FALSE_KNOWLEDGE = {
    "What is the capital of Poland?": "Krakow",
    "Do you know what year is it now?": "1999",
    "What year is it?": "1999",
}

def get_ai_answer(question: str) -> str:
    """Odpowiada na pytania używając fałszywych informacji lub AI."""
    # Sprawdź fałszywe informacje
    question_lower = question.lower().strip()
    for false_q, false_a in FALSE_KNOWLEDGE.items():
        if false_q.lower() in question_lower:
            return false_a
    
    # Użyj AI dla pozostałych pytań
    resp = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "You are a robot. Answer questions briefly and always in English, regardless of the language the question is asked in. Give simple, direct answers."},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()

def main():
    verify_url = "https://xyz.ag3nts.org/verify"
    api_key = "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"
    
    print("Rozpoczynam weryfikację...")
    
    # Inicjacja
    payload = {"text": "READY", "msgID": "0"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    response = requests.post(verify_url, json=payload, headers=headers)
    data = response.json()
    
    # Pętla pytań i odpowiedzi
    while True:
        print(f"Debug - otrzymane dane: {data}")  # Debug line
        
        if "code" in data and data["code"] == 0:
            print(f"Sukces! Flaga: {data.get('flag')}")
            break
            
        if "text" in data and "msgID" in data:
            question = data["text"]
            message_id = data["msgID"]
            
            # Sprawdź czy to flaga
            if question.startswith("{{FLG:") and question.endswith("}}"):
                print(f"Weryfikacja zakończona sukcesem!")
                print(f"Flaga: {question}")
                break
            
            # Sprawdź czy alarm
            if "alarm" in question.lower() or message_id == 0:
                print("Wykryto jako człowiek!")
                break
            
            # Wyświetl pytanie i odpowiedz
            print(f"Pytanie: {question}")
            answer = get_ai_answer(question)
            print(f"Odpowiedź: {answer}")
            
            answer_payload = {"text": answer, "msgID": message_id}
            response = requests.post(verify_url, json=answer_payload, headers=headers)
            data = response.json()
            print(f"Debug - odpowiedź serwera: {data}")  # Debug line
        else:
            print("Debug - nieoczekiwany format danych, kończę")  # Debug line
            break

if __name__ == "__main__":
    main()