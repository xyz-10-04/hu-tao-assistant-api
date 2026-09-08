
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# 1. 加载你本地的 chinese-roberta-wwm-ext-large 模型
# 注意：这里的路径指向你下载好的模型文件夹
# 如果你还没有这个模型，需要先从 Hugging Face 下载到本地
embedding_model = HuggingFaceEmbeddings(
    model_name="F:/AI_Projects/hutao/bert/chinese-roberta-wwm-ext-large",  # 替换成你实际的模型路径
    model_kwargs={'device': 'cpu'},  # 可以改成 'cuda' 如果显卡够用
    encode_kwargs={'normalize_embeddings': False}
)

# 2. 加载知识库文档
def load_documents():
    docs = []
    data_dir = "knowledge/"
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(data_dir, filename), encoding="utf-8")
            docs.extend(loader.load())
    return docs

# 3. 文本切分
def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=40,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    return text_splitter.split_documents(docs)

# 4. 构建 FAISS 向量库
def build_vectorstore(chunks):
    # FAISS 直接保存到本地目录，类似之前 ChromaDB 的 persist
    vectordb = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    # 保存到本地，方便下次直接加载
    vectordb.save_local("./faiss_index")
    return vectordb

# 5. 检索函数（供 Agent 调用）
def search_hu_tao(query, k=3):
    # 如果向量库已存在，直接加载；否则先构建
    if os.path.exists("./faiss_index"):
        vectordb = FAISS.load_local(
            "./faiss_index", 
            embedding_model,
            allow_dangerous_deserialization=True  # 因为是我们自己创建的，安全
        )
    else:
        docs = load_documents()
        chunks = split_documents(docs)
        vectordb = build_vectorstore(chunks)
    
    # 执行检索
    results = vectordb.similarity_search(query, k=k)
    return [doc.page_content for doc in results]


