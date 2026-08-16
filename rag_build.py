import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. 初始化ChromaDB（持久化）
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="huTao_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
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

# 3. 存入向量库
collection.add(
    documents=documents,
    ids=ids
)

# 4. 检索（手动）
def search(query, k=3):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results['documents'][0]  # 返回最相似的k个文档块

# 5. 生成（手动拼Prompt + 调用LLM API）
def ask(query):
    docs = search(query, k=3)
    context = "\n".join(docs)
    prompt = f"""基于以下信息回答问题：
    
{context}

问题：{query}
答案："""
    # 调用你的LLM API（你已经写过call_api了）
    return DEEPSEEK_API(prompt)

# 6. 查询
print(ask("胡桃的生日是哪天？"))