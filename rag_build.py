
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

import jieba

from bm25 import BM25, rrf_fusion, tokenize_zh, term_freq, doc_freq

def chinese_preprocess_func(text: str):
    return jieba.lcut(text)

# 1. 加载你本地的 bge-small-zh-v1.5 模型
# 注意：这里的路径指向你下载好的模型文件夹
# 如果你还没有这个模型，需要先从 Hugging Face 下载到本地
embedding_model = HuggingFaceEmbeddings(
    # 注意：复制你终端里输出的那个完整路径
    model_name="./models/models/BAAI--bge-small-zh-v1.5/snapshots/master",  
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}  # BGE 模型必须设为 True
)

# 2. 加载知识库文档
def load_documents(sub_dir=None):
    docs = []
    data_dir = "knowledge/"
    if sub_dir:
        data_dir = os.path.join(data_dir, sub_dir)
        
    # 如果指定了 sub_dir，或者没指定但根目录没文件，就递归遍历
    if sub_dir:
        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                loader = TextLoader(os.path.join(data_dir, filename), encoding="utf-8")
                docs.extend(loader.load())
    else:
        # 遍历 knowledge 下所有的子文件夹
        for root, dirs, files in os.walk(data_dir):
            for filename in files:
                if filename.endswith(".txt"):
                    filepath = os.path.join(root, filename)
                    loader = TextLoader(filepath, encoding="utf-8")
                    print(f"加载文件: {filename}")
                    docs.extend(loader.load())
    return docs
# 3. 文本切分
def split_documents(docs):
    chunks = []
    for doc in docs:
        source = doc.metadata["source"]
        
        # 最土的 if-else，绝对不会出错
        if "voice_lines" in source or "评价" in source:
            # 短文本：按段落切
            paragraphs = [p.strip() for p in doc.page_content.split("\n\n") if p.strip()]
            for p in paragraphs:
                from langchain_core.documents import Document
                chunks.append(Document(page_content=p, metadata=doc.metadata.copy()))
        else:
            # 长文本：用 splitter 切
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=300, chunk_overlap=50,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
            )
            chunks.extend(text_splitter.split_documents([doc]))
            
    # 加 doc_id
    for i, chunk in enumerate(chunks):
        filename = os.path.basename(chunk.metadata["source"]).removesuffix(".txt")
        # 注意：这里如果同一个文件产生多个 chunk，i 是全局递增的
        chunk.metadata["doc_id"] = f"{filename}_{i}"
        
    return chunks


# 4. 构建 FAISS 向量库
def build_vectorstore(chunks, index_path):
    vectordb = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    vectordb.save_local(index_path)   # ← 用传入的路径，而不是硬编码的 "./faiss_index"
    return vectordb


# 5. 检索函数（供 Agent 调用）
def search_hu_tao(query, k=10, category=None, return_ids=False):
    category_map = {
    "character": "角色评价",
    "story": "背景故事",
    "misc": "其他台词",
    }
    sub_dir = category_map.get(category) if category else None
    index_path = f"./faiss_index_{category}" if category else "./faiss_index"

    if os.path.exists(index_path):
        vectordb = FAISS.load_local(
            index_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        # 加载分类文档用于 BM25
        docs = load_documents(sub_dir)
        chunks = split_documents(docs)
    else:

        docs = load_documents(sub_dir)
        chunks = split_documents(docs)

        vectordb = build_vectorstore(chunks, index_path)

    # 6. 构建混合检索器
    # 构建 BM25（用分类 chunks）
    docs_dict = {chunk.metadata["doc_id"]: chunk.page_content for chunk in chunks}

    bm25 = BM25(docs_dict)
    bm25_results = bm25.search(query, top_k=10)


    faiss_retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    faiss_docs = faiss_retriever.invoke(query)
    faiss_results = [(doc.metadata["doc_id"], 0.0) for doc in faiss_docs]


    results = rrf_fusion([faiss_results, bm25_results])
    top_results = results[:k]

    if return_ids:
        return [(doc_id, score) for doc_id, score in top_results]
    
    return [docs_dict[doc_id] for doc_id, score in top_results]
