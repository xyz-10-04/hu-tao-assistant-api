
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

# 1. 加载你本地的 chinese-roberta-wwm-ext-large 模型
# 注意：这里的路径指向你下载好的模型文件夹
# 如果你还没有这个模型，需要先从 Hugging Face 下载到本地
embedding_model = HuggingFaceEmbeddings(
    model_name="../hutao/bert/chinese-roberta-wwm-ext-large",  # 替换成你实际的模型路径
    model_kwargs={'device': 'cpu'},  # 可以改成 'cuda' 如果显卡够用
    encode_kwargs={'normalize_embeddings': False}
)

# 2. 加载知识库文档
def load_documents(sub_dir=None):
    docs = []
    data_dir = "knowledge/"
    if sub_dir:
        data_dir = os.path.join(data_dir, sub_dir)
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(data_dir, filename), encoding="utf-8")
            print(f"加载文件: {filename}")
            docs.extend(loader.load())
    return docs

# 3. 文本切分
def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=90,
        chunk_overlap=10,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    return text_splitter.split_documents(docs)

# 4. 构建 FAISS 向量库
def build_vectorstore(chunks, index_path):
    vectordb = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    vectordb.save_local(index_path)   # ← 用传入的路径，而不是硬编码的 "./faiss_index"
    return vectordb

# 5. 构建混合检索器
def build_hybrid_retriever(chunks, vectordb):
     # BM25 检索器：关键词精确匹配
    bm25_retriever = BM25Retriever.from_documents(chunks, k=10)

    # FAISS 向量检索器：语义泛化
    faiss_retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # 融合：两个检索器各占一半权重
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.7, 0.3]
    )
    return ensemble_retriever

# 6. 检索函数（供 Agent 调用）
def search_hu_tao(query, k=10, category=None):
    category_map = {
        "food": "食物喜好",
        "character": "角色评价",
        "story": "背景故事",
        "misc": "台词杂项",
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
        print(f"【调试】开始构建 {category} 索引")
        docs = load_documents(sub_dir)
        chunks = split_documents(docs)
        print(f"【调试】加载了 {len(docs)} 个文档，切分为 {len(chunks)} 个块")
        vectordb = build_vectorstore(chunks, index_path)
        print(f"【调试】{category} FAISS 索引构建完成")

    # 构建 BM25（用分类 chunks）
    ensemble_retriever = build_hybrid_retriever(chunks, vectordb)
    results = ensemble_retriever.invoke(query)
    print(f"【调试】检索到 {len(results)} 个结果")
    return [doc.page_content for doc in results[:k]]
