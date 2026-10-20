from rag_build import load_documents, split_documents, embedding_model
from langchain_community.vectorstores import FAISS

# 强行建一次索引（因为刚刚删了）
docs = load_documents()
chunks = split_documents(docs)
vectordb = FAISS.from_documents(chunks, embedding_model)

print("=== 纯 FAISS 排名 ===")
for doc in vectordb.similarity_search("胡桃喜欢吃什么", k=3):
    print(doc.page_content[:40])