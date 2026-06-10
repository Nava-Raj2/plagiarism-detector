import re
import math
from collections import Counter
from difflib import SequenceMatcher

def preprocess(text):
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())

def tokenize(text):
    return preprocess(text).split()

def get_ngrams(tokens, n):
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def get_sentences(text):
    return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]

def jaccard_similarity(text1, text2, n=3):
    g1 = set(get_ngrams(tokenize(text1), n))
    g2 = set(get_ngrams(tokenize(text2), n))
    if not g1 and not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)

def cosine_similarity(text1, text2):
    freq1 = Counter(tokenize(text1))
    freq2 = Counter(tokenize(text2))
    words = set(freq1) | set(freq2)
    dot = sum(freq1[w] * freq2[w] for w in words)
    n1 = math.sqrt(sum(v**2 for v in freq1.values()))
    n2 = math.sqrt(sum(v**2 for v in freq2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

def lcs_ratio(text1, text2):
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def rolling_hash(ngram, base=31, mod=10**9+7):
    h = 0
    for char in " ".join(ngram):
        h = (h * base + ord(char)) % mod
    return h

def winnow_fingerprints(tokens, n=5, window=4):
    ngrams = get_ngrams(tokens, n)
    if not ngrams:
        return set()
    hashes = [rolling_hash(g) for g in ngrams]
    fingerprints = set()
    for i in range(len(hashes) - window + 1):
        fingerprints.add(min(hashes[i:i+window]))
    return fingerprints

def fingerprint_similarity(text1, text2):
    t1, t2 = tokenize(text1), tokenize(text2)
    fp1, fp2 = winnow_fingerprints(t1), winnow_fingerprints(t2)
    if not fp1 and not fp2:
        return 0.0
    return len(fp1 & fp2) / max(len(fp1), len(fp2))

def find_matching_phrases(text1, text2, threshold=0.4):
    sentences1 = get_sentences(text1)
    sentences2 = get_sentences(text2)
    matches = []
    for s1 in sentences1:
        for s2 in sentences2:
            if len(tokenize(s1)) < 5 or len(tokenize(s2)) < 5:
                continue
            sim = jaccard_similarity(s1, s2, n=3)
            if sim >= threshold:
                matches.append({"source": s1, "suspect": s2, "similarity": round(sim, 3)})
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches[:10]

def overall_score(text1, text2):
    jac3   = jaccard_similarity(text1, text2, n=3)
    jac2   = jaccard_similarity(text1, text2, n=2)
    cosine = cosine_similarity(text1, text2)
    fp_sim = fingerprint_similarity(text1, text2)
    lcs    = lcs_ratio(text1, text2)
    weighted = jac3 * 0.40 + cosine * 0.30 + fp_sim * 0.30
    pct = round(weighted * 100, 2)
    if pct >= 70:
        verdict = "High plagiarism — likely copied"
    elif pct >= 40:
        verdict = "Moderate similarity — manual review recommended"
    elif pct >= 15:
        verdict = "Low similarity — minor overlap"
    else:
        verdict = "Very low similarity — likely original"
    return {
        "overall_score_pct": pct,
        "verdict": verdict,
        "metrics": {
            "jaccard_3gram": round(jac3 * 100, 2),
            "jaccard_2gram": round(jac2 * 100, 2),
            "cosine_similarity": round(cosine * 100, 2),
            "fingerprint_similarity": round(fp_sim * 100, 2),
            "lcs_ratio": round(lcs * 100, 2),
        },
        "matching_phrases": find_matching_phrases(text1, text2),
    }
