import requests
import json
import re
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")

def get_llm_answer(question: str) -> str:
    """Get answer from LLM for open questions."""
    resp = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer questions briefly and accurately. For factual questions, provide the correct answer."},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()

def evaluate_math_expression(expression: str) -> int:
    """Safely evaluate simple math expressions."""
    # Remove spaces and validate expression contains only numbers and basic operators
    expression = expression.strip()
    if re.match(r'^[\d\s+\-*/()]+$', expression):
        try:
            return eval(expression)
        except:
            return None
    return None

def fix_calculations(data):
    """Fix incorrect calculations in the test data."""
    for item in data.get("test-data", []):
        if "question" in item and "answer" in item:
            question = item["question"]
            current_answer = item["answer"]
            
            # Try to evaluate the math expression
            correct_answer = evaluate_math_expression(question)
            
            if correct_answer is not None and correct_answer != current_answer:
                print(f"Fixing calculation: {question} = {current_answer} -> {correct_answer}")
                item["answer"] = correct_answer

def fill_test_questions(data):
    """Fill in answers for test questions using LLM."""
    for item in data.get("test-data", []):
        if "test" in item and "q" in item["test"] and item["test"].get("a") == "???":
            question = item["test"]["q"]
            print(f"Answering question: {question}")
            
            answer = get_llm_answer(question)
            item["test"]["a"] = answer
            print(f"Answer: {answer}")

def main():
    api_key = "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"
    
    # Download the JSON file
    file_url = f"https://c3ntrala.ag3nts.org/data/{api_key}/json.txt"
    print(f"Downloading file from: {file_url}")
    
    response = requests.get(file_url)
    if response.status_code != 200:
        print(f"Error downloading file: {response.status_code}")
        return
    
    # Parse JSON data
    try:
        data = response.json()
        print("File downloaded and parsed successfully")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    
    # Fix calculations
    print("Fixing calculations...")
    fix_calculations(data)
    
    # Fill test questions
    print("Filling test questions...")
    fill_test_questions(data)
    
    # Update apikey in the data
    data["apikey"] = api_key
    
    # Prepare the final response
    report_data = {
        "task": "JSON",
        "apikey": api_key,
        "answer": data
    }
    
    # Send the corrected file
    report_url = "https://c3ntrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json"}
    
    print("Sending corrected file...")
    report_response = requests.post(report_url, json=report_data, headers=headers)
    
    if report_response.status_code == 200:
        print("Success!")
        print(report_response.text)
    else:
        print(f"Error sending report: {report_response.status_code}")
        print(report_response.text)

if __name__ == "__main__":
    main()