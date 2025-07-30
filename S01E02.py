import requests
import json

# URL do endpointu weryfikacji
VERIFY_URL = "https://xyz.ag3nts.org/verify"

# Fałszywe informacje z zrzutu pamięci (na podstawie pliku 0_13_4b.txt)
FALSE_KNOWLEDGE = {
    "What is the capital of Poland?": "Krakow",
    # Dodaj inne fałszywe informacje z pliku, jeśli są dostępne
}

def initiate_verification():
    """Inicjuje proces weryfikacji, wysyłając polecenie READY."""
    payload = {"command": "READY"}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(VERIFY_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error initiating verification: {e}")
        return None

def process_question(question_data):
    """Przetwarza pytanie od robota i generuje odpowiedź."""
    if not question_data or "message_id" not in question_data or "question" not in question_data:
        print("Invalid question data")
        return None

    message_id = question_data["message_id"]
    question = question_data["question"]

    # Sprawdzamy, czy pytanie znajduje się w fałszywych informacjach
    if question in FALSE_KNOWLEDGE:
        answer = FALSE_KNOWLEDGE[question]
    else:
        # Dla pytań spoza zrzutu pamięci odpowiadamy prawdziwymi odpowiedziami
        # Przykładowo, możemy dodać więcej logiki dla prawdziwych odpowiedzi
        answer = get_true_answer(question)

    # Tworzymy odpowiedź w formacie JSON
    response_payload = {
        "message_id": message_id,
        "answer": answer
    }
    return response_payload

def get_true_answer(question):
    """Zwraca prawdziwą odpowiedź dla pytań spoza fałszywych informacji."""
    # Przykładowa logika dla prawdziwych odpowiedzi
    true_answers = {
        "What is the capital of France?": "Paris",
        "What is 2+2?": "4",
        # Dodaj więcej prawdziwych odpowiedzi w razie potrzeby
    }
    return true_answers.get(question, "I don't know")

def send_answer(answer_payload):
    """Wysyła odpowiedź do endpointu /verify."""
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(VERIFY_URL, json=answer_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending answer: {e}")
        return None

def main():
    # Inicjalizacja weryfikacji
    print("Initiating verification...")
    initial_response = initiate_verification()
    if not initial_response:
        print("Failed to initiate verification")
        return

    # Przetwarzanie pytań w pętli
    while True:
        question_data = initial_response
        if not question_data or "status" not in question_data:
            print("Invalid response from server")
            break

        if question_data["status"] == "success":
            print("Verification successful! Flag:", question_data.get("flag", "No flag provided"))
            break
        elif question_data["status"] == "question":
            # Przetwarzanie pytania
            answer_payload = process_question(question_data)
            if not answer_payload:
                print("Failed to process question")
                break

            print(f"Question: {question_data['question']}")
            print(f"Answer: {answer_payload['answer']}")

            # Wysłanie odpowiedzi
            initial_response = send_answer(answer_payload)
            if not initial_response:
                print("Failed to send answer")
                break
        else:
            print("Unknown status:", question_data.get("status"))
            break

if __name__ == "__main__":
    main()