import requests
import os
import re
import json
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from openai import OpenAI
from PIL import Image
from io import BytesIO

API_KEY = "b76d036a-560e-48a2-b895-7f7fb0115cec"
OPENAI_KEY = "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"

ARTICLE_URL = "https://c3ntrala.ag3nts.org/dane/arxiv-draft.html"
QUESTIONS_URL = f"https://c3ntrala.ag3nts.org/data/{API_KEY}/arxiv.txt"
REPORT_URL = "https://c3ntrala.ag3nts.org/report"

client = OpenAI(api_key=OPENAI_KEY)

CACHE_DIR = "arxiv_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def make_absolute_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"https://c3ntrala.ag3nts.org/dane/{url.lstrip('/')}"

def download_file(url, fname):
    abs_url = make_absolute_url(url)
    path = os.path.join(CACHE_DIR, fname)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    resp = requests.get(abs_url)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    return resp.content

def describe_image(img_url, caption):
    fname = os.path.basename(img_url)
    cache_path = os.path.join(CACHE_DIR, fname + ".desc.txt")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    abs_url = make_absolute_url(img_url)
    prompt = f"Describe this image in one or two sentences. Context: {caption}"
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Describe images briefly and precisely."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": abs_url}}
                ]
            }
        ],
        max_tokens=120
    )
    desc = resp.choices[0].message.content.strip()
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(desc)
    return desc

def transcribe_audio(audio_url):
    fname = os.path.basename(audio_url)
    audio_bytes = download_file(audio_url, fname)
    cache_path = os.path.join(CACHE_DIR, fname + ".txt")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=BytesIO(audio_bytes),
        response_format="text"
    )
    transcript = resp.strip()
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    return transcript

def extract_article():
    html = requests.get(ARTICLE_URL).text
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt", "")
        caption = ""
        if img.parent.name == "figure":
            cap = img.parent.find("figcaption")
            if cap:
                caption = cap.get_text(strip=True)
        elif img.next_sibling and img.next_sibling.name in ["figcaption", "span"]:
            caption = img.next_sibling.get_text(strip=True)
        images.append({"src": src, "alt": alt, "caption": caption})
    audios = []
    for audio in soup.find_all("audio"):
        src = audio.get("src")
        if src:
            audios.append({"src": src})
    for tag in soup(["script", "style"]):
        tag.decompose()
    text_md = md(str(soup.body))
    return text_md, images, audios

def build_markdown(text_md, images, audios):
    md_parts = [text_md, "\n\n## Image descriptions\n"]
    for img in images:
        desc = describe_image(img["src"], img["caption"])
        md_parts.append(f"**Image:** {img['caption'] or img['alt']}\n{desc}\n")
    if audios:
        md_parts.append("\n## Audio transcriptions\n")
        for audio in audios:
            transcript = transcribe_audio(audio["src"])
            md_parts.append(f"**Audio:** {audio['src']}\n{transcript}\n")
    return "\n".join(md_parts)

def get_questions():
    resp = requests.get(QUESTIONS_URL)
    resp.raise_for_status()
    print("Pobrane pytania:\n", resp.text)  # DEBUG
    questions = {}
    for line in resp.text.splitlines():
        print("LINIA:", line)  # DEBUG
        m = re.match(r"^(\d+)[\.\:\-=]\s*(.+)", line)
        if m:
            questions[m.group(1)] = m.group(2)
    print("Znalezione pytania:", questions)  # DEBUG
    if not questions:
        print("Nie znaleziono żadnych pytań! Sprawdź format pliku z pytaniami.")
        exit(1)
    return questions

def answer_questions(questions, context_md, feedback=None, images=None, audios=None, text_md=None):
    answers = {}
    for qid, qtext in questions.items():
        extra_context = ""
        if feedback and qid in feedback:
            extra_context = (
                f"\nPrevious answer for this question was: '{feedback[qid]}' and it was incorrect. "
                "Do not repeat this answer. Answer differently."
            )
        # Zbuduj kontekst: opisy obrazów, transkrypcje, tekst (wszystko, ale nie powielaj)
        img_desc = ""
        if images:
            for img in images:
                desc = describe_image(img["src"], img["caption"])
                if desc.strip():
                    img_desc += f"- {desc.strip()}\n"
        audio_desc = ""
        if audios:
            for audio in audios:
                transcript = transcribe_audio(audio["src"])
                if transcript.strip():
                    audio_desc += f"- {transcript.strip()}\n"
        # Prompt: AI ma korzystać z kontekstu, nie zgadywać!
        prompt = (
            "Odpowiedz na pytanie na podstawie poniższego artykułu, opisów obrazów i transkrypcji audio. "
            "Jeśli odpowiedź jest w opisie obrazu lub transkrypcji, użyj jej. "
            "Jeśli nie, użyj tekstu artykułu. Odpowiadaj jednym krótkim, precyzyjnym zdaniem.\n\n"
            f"OPISY OBRAZÓW:\n{img_desc}\n"
            f"TRANSKRYPCJE AUDIO:\n{audio_desc}\n"
            f"TEKST ARTYKUŁU:\n{text_md[:2000] if text_md else ''}\n\n"
            f"PYTANIE: {qtext}{extra_context}\nODPOWIEDŹ:"
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem. Odpowiadaj zwięźle i precyzyjnie, jednym zdaniem."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120
        )
        answer = resp.choices[0].message.content.strip()
        answers[qid] = answer
    return answers

def main():
    print("Extracting article...")
    text_md, images, audios = extract_article()
    print("Building markdown context...")
    context_md = build_markdown(text_md, images, audios)
    MAX_CONTEXT_LEN = 4000
    if len(context_md) > MAX_CONTEXT_LEN:
        context_md = context_md[:MAX_CONTEXT_LEN]
    print("Getting questions...")
    questions = get_questions()
    feedback = {}
    max_attempts = 5  # Uniwersalny limit prób
    attempt = 0
    while attempt < max_attempts:
        print(f"Answering questions... (attempt {attempt+1})")
        answers = answer_questions(questions, context_md, feedback, images, audios, text_md)
        print("Odpowiedzi:", answers)
        result = {
            "task": "arxiv",
            "apikey": API_KEY,
            "answer": answers
        }
        print("Sending report...")
        resp = requests.post(REPORT_URL, json=result, headers={"Content-Type": "application/json"})
        print("Status:", resp.status_code)
        print(resp.text)
        if resp.status_code == 200:
            print("Sukces! Zadanie zaliczone.")
            break
        try:
            data = resp.json()
            if data.get("code") == -304:
                m = re.search(r"question (\d+)", data.get("message", ""))
                if m:
                    qid = m.group(1).zfill(2)
                    feedback[qid] = answers[qid]
                    print(f"Poprawiam odpowiedź na pytanie {qid}...")
                else:
                    print("Nie można zidentyfikować błędnego pytania, przerywam.")
                    break
            else:
                print("Inny błąd serwera, przerywam.")
                break
        except Exception:
            print("Błąd podczas przetwarzania odpowiedzi serwera, przerywam.")
            break
        attempt += 1
    else:
        print("Nie udało się uzyskać poprawnych odpowiedzi po kilku próbach. Sprawdź artykuł i pytania ręcznie.")

if __name__ == "__main__":
    main()