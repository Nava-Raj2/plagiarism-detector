import re
import math
import urllib.request
import urllib.parse
import json
from collections import Counter
from html.parser import HTMLParser

API_KEY = "071f69b24a714161ae793b16cd10d5773bcd22bbdff83c021008fd48f30b7449"

def clean(text):
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())

def tokenize(text):
    return clean(text).split()

def cosine_similarity(t1, t2):
    f1, f2 = Counter(tokenize(t1)), Counter(tokenize(t2))
    words = set(f1) | set(f2)
    dot = sum(f1[w] * f2[w] for w in words)
    n1 = math.sqrt(sum(v**2 for v in f1.values()))
    n2 = math.sqrt(sum(v**2 for v in f2.values()))
    return dot / (n1 * n2) if n1 and n2 else 0.0

def extract_phrases(text, n=8):
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 30]
    phrases = []
    for s in sentences[:10]:
        words = s.split()
        if len(words) >= n:
            mid = len(words) // 2
            start = max(0, mid - n // 2)
            phrases.append(" ".join(words[start:start + n]))
    return list(dict.fromkeys(phrases))[:5]

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer", "header"):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "header"):
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

def fetch_page_text(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="ignore")
        parser = TextExtractor()
        parser.feed(raw)
        text = " ".join(parser.text)
        return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return ""

def serpapi_search(query, api_key, num=5):
    params = urllib.parse.urlencode({
        "q": query,
        "api_key": api_key,
        "num": num,
        "engine": "google"
    })
    url = f"https://serpapi.com/search?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        results = []
        for item in data.get("organic_results", []):
            results.append({
                "link":    item.get("link", ""),
                "title":   item.get("title", ""),
                "snippet": item.get("snippet", ""),
            })
        return results
    except Exception as e:
        print(f"  [Search error] {e}")
        return []

def check_plagiarism(text, api_key=API_KEY):
    print("\nExtracting key phrases...")
    phrases = extract_phrases(text)
    if not phrases:
        return {"error": "Text too short — please provide at least 3-4 sentences."}
    print(f"Found {len(phrases)} phrases to search\n")
    all_matches = []
    seen_urls = set()
    for i, phrase in enumerate(phrases, 1):
        print(f"Searching ({i}/{len(phrases)}): \"{phrase[:60]}...\"")
        results = serpapi_search(phrase, api_key)
        for item in results:
            url     = item.get("link", "")
            title   = item.get("title", "")
            snippet = item.get("snippet", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            snippet_sim = cosine_similarity(text[:500], snippet)
            page_sim = 0.0
            if snippet_sim > 0.1:
                print(f"  Fetching: {url[:70]}...")
                page_text = fetch_page_text(url)
                if page_text:
                    page_sim = cosine_similarity(text, page_text[:5000])
            final_sim = max(snippet_sim, page_sim)
            if final_sim > 0.05:
                all_matches.append({
                    "url":        url,
                    "title":      title,
                    "similarity": round(final_sim * 100, 1),
                    "snippet":    snippet[:200],
                })
    all_matches.sort(key=lambda x: x["similarity"], reverse=True)
    top_matches = all_matches[:5]
    overall = top_matches[0]["similarity"] if top_matches else 0.0
    if overall >= 70:
        verdict = "High plagiarism detected"
    elif overall >= 40:
        verdict = "Moderate similarity — review recommended"
    elif overall >= 15:
        verdict = "Low similarity — minor overlap"
    else:
        verdict = "No significant plagiarism found"
    return {
        "overall_score": overall,
        "verdict":       verdict,
        "total_sources": len(all_matches),
        "top_matches":   top_matches,
    }

def print_report(result):
    if "error" in result:
        print(f"\nError: {result['error']}")
        return
    print("\n" + "=" * 60)
    print("        INTERNET PLAGIARISM REPORT")
    print("=" * 60)
    print(f"  Overall Score  : {result['overall_score']}%")
    print(f"  Verdict        : {result['verdict']}")
    print(f"  Sources checked: {result['total_sources']}")
    if result["top_matches"]:
        print("\n" + "-" * 60)
        print("  Top Matching Sources")
        print("-" * 60)
        for i, m in enumerate(result["top_matches"], 1):
            print(f"\n  [{i}] {m['similarity']}% match")
            print(f"      Title   : {m['title'][:70]}")
            print(f"      URL     : {m['url'][:70]}")
            print(f"      Snippet : {m['snippet'][:120]}...")
    else:
        print("  No matching sources found online.")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("       INTERNET PLAGIARISM CHECKER")
    print("=" * 60)
    print("Paste your text below, then press Enter and type END.")
    print("-" * 60)
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        print("No text entered. Exiting.")
    else:
        result = check_plagiarism(text)
        print_report(result)
