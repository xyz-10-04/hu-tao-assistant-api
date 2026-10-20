import jieba
import math
import re

def tokenize_zh(text: str) -> list[str]:
    tokens = jieba.lcut(text)
    result = []
    for t in tokens:
        t = t.strip()
        if re.match(r'^[\W_]+$', t):
            continue
        if not t:
            continue
        result.append(t)
    return result

def term_freq(tokens: list[str]) -> dict[str, int]:
    result = {}
    for t in tokens:
        if t in result:
            result[t] += 1
        else:
            result[t] = 1
    return result


def doc_freq(docs: dict[str, str]) -> dict[str, int]:
    result = {}
    for text in docs.values():
        tokens = tokenize_zh(text)
        for t in set(tokens):
            if t in result:
                result[t] += 1
            else:
                result[t] = 1
    return result


class BM25:
    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.N = len(self.docs)
        self.tokenized = {doc_id: tokenize_zh(text) for doc_id, text in self.docs.items()}
        self.doc_len = {doc_id: len(tokens) for doc_id, tokens in self.tokenized.items()}
        self.df = doc_freq(self.docs)
        self.avg_len = sum(self.doc_len.values()) / (self.N or 1)
        self.tf = {doc_id: term_freq(tokens) for doc_id, tokens in self.tokenized.items()}

    def _score(self, query_tokens: list[str], doc_id: str) -> float:
        score = 0.0
        for q in query_tokens:
            tf = self.tf[doc_id].get(q, 0)
            if tf == 0:
                continue
            idf = math.log((self.N - self.df[q] + 0.5) / (self.df[q] + 0.5) + 1)    #公式不确定
            tf_component = ((tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * self.doc_len[doc_id] / self.avg_len)))   #公式不确定
            score += idf * tf_component
        return score

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if not query or not self.docs:
            return []
        tokens = tokenize_zh(query)
        score = [(doc_id, self._score(tokens, doc_id)) for doc_id in self.docs]   #公式不确定
        sorted_result = sorted(score, key=lambda x: x[1], reverse=True)
        return sorted_result[:top_k]

    
bm25 = BM25({"d1": "胡桃 喜欢 杏仁豆腐", "d2": "胡桃 甜点"})
print(bm25._score(["胡桃"], "d1"))     # 0.1673
print(bm25._score(["胡桃"], "d2"))     # 0.2004
print(bm25._score(["杏仁豆腐"], "d1"))  # 0.6359
print(bm25._score(["杏仁豆腐"], "d2"))  # 0.0