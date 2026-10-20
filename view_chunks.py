from rag_build import load_documents, split_documents

cat_map = {"misc": "其他台词", "character": "角色评价", "story": "背景故事"}
for cat, sub_dir in cat_map.items():
    print(f"\n===== {cat} =====")
    docs = load_documents(sub_dir=sub_dir)
    chunks = split_documents(docs)
    for c in chunks:
        print(f"[{c.metadata['doc_id']}] {c.page_content[:60]}")