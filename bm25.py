import jieba
import re
import math

def tokenize_zh(text: str) -> list[str]:
    result = []
    tokens = jieba.lcut(text)
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
        uniques_tokens = set(tokens)
        for t in uniques_tokens:
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
        self.tokenized = {doc_id: tokenize_zh(text) for doc_id, text in docs.items()}
        self.doc_len = {doc_id: len(self.tokenized[doc_id]) for doc_id in docs}
        self.df = doc_freq(docs) 
        self.avg_len = sum(self.doc_len.values()) / (self.N or 1)
        self.tf = {doc_id: term_freq(tokens) for doc_id, tokens in self.tokenized.items()}


    def _score(self, query_tokens: list[str], doc_id: str) -> float:
        """算一篇文档对 query 的 BM25 得分。"""
        score = 0.0
        for q in query_tokens:
            tf = self.tf[doc_id].get(q, 0)
            if tf == 0:
                continue
            idf = math.log((self.N - self.df[q] + 0.5) / (self.df[q] + 0.5) + 1)
            tf_component = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * self.doc_len[doc_id] / self.avg_len)
                )
            score += idf * tf_component

        return score


    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if not query or not self.docs:
            return []
        query_tokens = tokenize_zh(query)
        result = [(doc_id, self._score(query_tokens, doc_id)) for doc_id in self.docs]
        top = sorted(result, key=lambda x: x[1], reverse = True)
        return top[:top_k]


def rrf_fusion(result_lists: 
    list[list[tuple[str, float]]],
    k: int = 60,
    ) -> list[tuple[str, float]]:
    rrf_score = {}
    for r in result_lists:
        for rank, (doc_id, score) in enumerate(r):   
            if doc_id in rrf_score:    
                rrf_score[doc_id] += 1 / (k + rank)   
            else:
                rrf_score[doc_id] = 1 / (k + rank)
    sorted_result = sorted(rrf_score.items(), key=lambda x: x[1], reverse=True)
    return sorted_result


