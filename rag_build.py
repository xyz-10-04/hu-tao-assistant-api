import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import numpy as np
from api import call_api  # 导入你已有的 API 调用函数

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 1. 初始化 ChromaDB（持久化）
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="huTao_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"  # ✅ 多语言模型
    )
)

# 2. 准备文档（手动切分）
documents = [
    "胡桃是往生堂第七十七代堂主，性格活泼开朗。",
    "胡桃的生日是7月15日。",
    "胡桃的武器是护摩之杖。",
    # ... 更多文档块
]
ids = [f"doc_{i}" for i in range(len(documents))]

# 3. 存入向量库（首次运行添加，后续注释掉或清空再添加）
# 如果集合已有数据，先清空
try:
    existing_ids = collection.get()['ids']
    if existing_ids:
        collection.delete(ids=existing_ids)
except Exception:
    pass

collection.add(
    documents=documents,
    ids=ids
)

# 4. 检索
def search_hu_tao(query, k=2):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results['documents'][0]

# 5. 生成（调用已有的 call_api）
def ask(query):
    docs = search_hu_tao(query, k=2)
    context = "\n".join(docs)
    prompt = f"""基于以下信息回答问题：

{context}

问题：{query}
答案："""
    
    response = call_api(prompt)  # 调用你已有的 API 函数
    return response.choices[0].message.content

# 6. 查询
if __name__ == "__main__":
    print(ask("胡桃的生日是哪天？"))