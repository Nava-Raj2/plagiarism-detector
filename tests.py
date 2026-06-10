import pytest
from detector import (
    tokenize, get_ngrams, jaccard_similarity,
    cosine_similarity, lcs_ratio, fingerprint_similarity,
    find_matching_phrases, overall_score
)

ORIGINAL = "Machine learning is a branch of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves. The process begins with observations or data, such as examples, direct experience, or instruction."

COPIED = "Machine learning is a branch of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves."

PARAPHRASED = "ML is a subfield of AI that allows computers to improve through experience rather than through explicit instruction. It is concerned with building programs capable of self-learning from data."

UNRELATED = "The French Revolution began in 1789 and fundamentally transformed the political landscape of Europe. Driven by Enlightenment ideals of liberty, equality, and fraternity, the revolutionaries abolished the monarchy."

def test_tokenize_basic():
    assert tokenize("Hello, World!") == ["hello", "world"]

def test_tokenize_empty():
    assert tokenize("") == []

def test_ngrams():
    tokens = ["a", "b", "c", "d"]
    assert get_ngrams(tokens, 3) == [("a","b","c"), ("b","c","d")]

def test_jaccard_identical():
    assert jaccard_similarity(ORIGINAL, ORIGINAL) > 0.99

def test_jaccard_high():
    assert jaccard_similarity(ORIGINAL, COPIED) > 0.60

def test_jaccard_low():
    assert jaccard_similarity(ORIGINAL, UNRELATED) < 0.10

def test_cosine_identical():
    assert cosine_similarity(ORIGINAL, ORIGINAL) > 0.99

def test_cosine_copied():
    assert cosine_similarity(ORIGINAL, COPIED) > 0.80

def test_cosine_unrelated():
    assert cosine_similarity(ORIGINAL, UNRELATED) < 0.25

def test_overall_structure():
    result = overall_score(ORIGINAL, COPIED)
    assert "overall_score_pct" in result
    assert "verdict" in result
    assert "metrics" in result

def test_overall_high_for_copy():
    result = overall_score(ORIGINAL, COPIED)
    assert result["overall_score_pct"] > 50

def test_overall_low_for_unrelated():
    result = overall_score(ORIGINAL, UNRELATED)
    assert result["overall_score_pct"] < 15
