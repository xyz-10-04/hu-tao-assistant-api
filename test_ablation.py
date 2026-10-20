from rag_build import load_documents, split_documents, embedding_model
from bm25 import BM25, rrf_fusion
from langchain_community.vectorstores import FAISS
from rag_build import search_hu_tao


# 准备数据
docs = load_documents(sub_dir="其他台词")
chunks = split_documents(docs)
docs_dict = {c.metadata["doc_id"]: c.page_content for c in chunks}

# 1. 只跑 BM25 的结果
bm25 = BM25(docs_dict)
print("--- 纯 BM25 ---")
print(bm25.search("胡桃喜欢吃什么", top_k=3))

# 2. 只跑 FAISS 的结果
vectordb = FAISS.load_local("./faiss_index_misc", embedding_model, allow_dangerous_deserialization=True)
print("--- 纯 FAISS ---")
faiss_docs = vectordb.similarity_search("胡桃喜欢吃什么", k=3)
for d in faiss_docs:
    print(d.metadata["doc_id"])

# 3. 看 RRF 融合后的结果
print("--- 混合检索 (RRF) ---")
print(search_hu_tao("胡桃喜欢吃什么", k=3, category="misc", return_ids=True))