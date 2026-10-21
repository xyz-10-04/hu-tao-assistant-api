from rag_build import load_documents, split_documents

cat_map = {"misc": "其他台词"}
docs = load_documents(sub_dir="其他台词")
chunks = split_documents(docs)

for c in chunks:
    print(f"\n[{c.metadata['doc_id']}]")
    print(c.page_content)
    print("-" * 40)