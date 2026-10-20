
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from rag_build import search_hu_tao

questions = []
with open("eval/questions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        questions.append(json.loads(line))

def is_hit(retrieved_ids, expected_ids, k):
    return any(did in retrieved_ids for did in expected_ids[:k])

total_questions = len(questions) 
hits_at_1 = 0
hits_at_3 = 0
hits_at_5 = 0

for q in questions:
    retrieved = search_hu_tao(q["question"], k=5, category=q.get("category"), return_ids=True)
    retrieved_ids = [doc_id for doc_id, score in retrieved]

    if is_hit(retrieved_ids, q["expected_doc_ids"], 1):
        hits_at_1 += 1
    if is_hit(retrieved_ids, q["expected_doc_ids"], 3):
        hits_at_3 += 1
    if is_hit(retrieved_ids, q["expected_doc_ids"], 5):
        hits_at_5 += 1

        # 找出前3名没命中的错题
    if not is_hit(retrieved_ids, q["expected_doc_ids"], 3):
        print(f"\n❌ 失败案例: {q['id']} - {q['question']}")
        print(f"期望: {q['expected_doc_ids']}")
        print(f"实际返回: {retrieved_ids}")



print(f"总问题数: {total_questions}")
print(f"Recall@1: {hits_at_1 / total_questions:.2%}")
print(f"Recall@3: {hits_at_3 / total_questions:.2%}")
print(f"Recall@5: {hits_at_5 / total_questions:.2%}")
