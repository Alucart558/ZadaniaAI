import requests
import json
import time

API_KEY = "b76d036a-560e-48a2-b895-7f7fb0115cec"
API_DB_URL = "https://c3ntrala.ag3nts.org/apidb"
API_CENTRAL_URL = "https://c3ntrala.ag3nts.org/report"

def query_db(sql):
    payload = {
        "task": "database",
        "apikey": API_KEY,
        "query": sql
    }
    r = requests.post(API_DB_URL, json=payload)
    r.raise_for_status()
    return r.json()

def get_table_schema(table_name):
    sql = f"SHOW CREATE TABLE {table_name};"
    resp = query_db(sql)
    return resp

def get_tables():
    resp = query_db("SHOW TABLES;")
    return resp

def get_sql_query_from_llm(schemas):
    # Poprawione zapytanie SQL zgodnie ze schematem bazy
    return "SELECT d.dc_id FROM datacenters d JOIN users u ON d.manager = u.id WHERE d.is_active = 1 AND u.is_active = 0;"

def extract_ids_from_result(result):
    # result['reply'] to lista słowników z kluczem 'dc_id'
    return [int(row['dc_id']) for row in result.get('reply', []) if 'dc_id' in row]

def send_answer_to_central(answer):
    payload = {
        "task": "database",
        "apikey": API_KEY,
        "answer": answer
    }
    r = requests.post(API_CENTRAL_URL, json=payload)
    print("CENTRALA:", r.status_code, r.text)
    return r.status_code, r.text

def main():
    # 1. Odkryj tabele i schematy (logowanie dla debugowania)
    print("Pobieram listę tabel...")
    tables = get_tables()
    print("Tabele:", tables)
    for t in ['users', 'datacenters']:
        print(f"Schemat {t}:")
        schema = get_table_schema(t)
        print(schema)
        time.sleep(0.5)

    # 2. Wygeneruj zapytanie SQL (tu: ręcznie, na podstawie schematów)
    schemas = {}  # Możesz przekazać schematy do LLM, jeśli chcesz
    sql = get_sql_query_from_llm(schemas)
    print("SQL:", sql)

    # 3. Wykonaj zapytanie SQL
    result = query_db(sql)
    print("Wynik SQL:", result)

    # 4. Wyciągnij listę ID
    ids = extract_ids_from_result(result)
    print("ID aktywnych datacenter zarządzanych przez nieaktywnych menadżerów:", ids)

    # 5. Wyślij odpowiedź do centrali
    send_answer_to_central(ids)

if __name__ == "__main__":
    main()