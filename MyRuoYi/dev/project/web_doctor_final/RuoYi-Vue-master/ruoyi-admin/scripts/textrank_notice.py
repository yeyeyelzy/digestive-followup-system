#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import re
import sys
from collections import Counter, defaultdict


def split_sentences(text):
    parts = re.split(r"[。！？!?；;\n\r]+", text)
    return [p.strip() for p in parts if p and p.strip()]


def sentence_tokens(sentence):
    words = re.findall(r"[\u4e00-\u9fff]+|[A-Za-z0-9]+", sentence)
    tokens = []
    for w in words:
        if re.fullmatch(r"[\u4e00-\u9fff]+", w):
            if len(w) <= 2:
                tokens.append(w)
            else:
                tokens.extend([w[i : i + 2] for i in range(len(w) - 1)])
        else:
            tokens.append(w.lower())
    return [t for t in tokens if t]


def build_sentence_vectors(sentences):
    vectors = []
    for s in sentences:
        vectors.append(Counter(sentence_tokens(s)))
    return vectors


def cosine_similarity(v1, v2):
    if not v1 or not v2:
        return 0.0
    common = set(v1.keys()) & set(v2.keys())
    dot = sum(v1[k] * v2[k] for k in common)
    n1 = math.sqrt(sum(x * x for x in v1.values()))
    n2 = math.sqrt(sum(x * x for x in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def textrank_sentences(sentences, damping=0.85, max_iter=80, tol=1e-5):
    n = len(sentences)
    if n == 0:
        return []
    if n == 1:
        return [0]

    vectors = build_sentence_vectors(sentences)
    graph = defaultdict(dict)

    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(vectors[i], vectors[j])
            if sim > 0:
                graph[i][j] = sim
                graph[j][i] = sim

    scores = [1.0] * n
    for _ in range(max_iter):
        next_scores = [(1.0 - damping)] * n
        for i in range(n):
            for j, w_ji in graph[i].items():
                out_sum = sum(graph[j].values())
                if out_sum > 0:
                    next_scores[i] += damping * (w_ji / out_sum) * scores[j]
        delta = max(abs(next_scores[i] - scores[i]) for i in range(n))
        scores = next_scores
        if delta < tol:
            break

    ranked = sorted(range(n), key=lambda i: scores[i], reverse=True)
    return ranked


def summarize_notice(text, max_sentences=5):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return text.strip()

    ranked = textrank_sentences(sentences)
    top_n = max(1, min(max_sentences, len(sentences)))
    selected = sorted(ranked[:top_n])
    return "；".join(sentences[i] for i in selected)


def main():
    notice = ""
    if len(sys.argv) > 1:
        notice = sys.argv[1]

    notice = (notice or "").strip()
    if not notice:
        print("")
        return

    result = summarize_notice(notice)
    print(result)


if __name__ == "__main__":
    main()
