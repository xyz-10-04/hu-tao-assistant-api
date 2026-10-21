import json
from rag_build import load_documents, split_documents

cat_map = {"misc": "其他台词", "character": "角色评价", "story": "背景故事"}

# 收集所有真实存在的 doc_id
all_ids = set()
for cat, sub_dir in cat_map.items():
    docs = load_documents(sub_dir=sub_dir)
    chunks = split_documents(docs)
    for c in chunks:
        all_ids.add(c.metadata["doc_id"])

# 读评测集，检查每个 expected_doc_id
with open("eval/questions.jsonl", encoding="utf-8") as f:
    for line in f:
        q = json.loads(line)
        for did in q["expected_doc_ids"]:
            if did not in all_ids:
                print(f"❌ {q['id']} 的 {did} 不存在")
            else:
                print(f"✓ {q['id']} 的 {did} 存在")