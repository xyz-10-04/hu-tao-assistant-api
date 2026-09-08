import os
from dotenv import load_dotenv
# 1. 文本分割器：从 langchain-text-splitters 导入
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 2. 文档加载器：从 langchain-community 导入
from langchain_community.document_loaders import TextLoader
# 3. 向量数据库：从 langchain-community 导入
from langchain_community.vectorstores import Chroma
# 4. 嵌入模型：从 langchain-openai 导入
from langchain_openai import OpenAIEmbeddings
# 5. LLM 模型：从 langchain-openai 导入
from langchain_openai import ChatOpenAI
# 6. 核心链组件：从 langchain_classic 导入，而不是 langchain
from langchain_classic.chains import RetrievalQA

load_dotenv()
# ... 后续代码不变 ...

# 1. 加载知识库文档
def load_documents():
    docs = []
    data_dir = "knowledge/"
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(data_dir, filename), encoding="utf-8")
            docs.extend(loader.load())
    return docs

# 2. 文本切分
def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    return text_splitter.split_documents(docs)

# 3. 构建向量数据库
def build_vectorstore(chunks):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base="https://api.deepseek.com"
    )
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    vectordb.persist()
    return vectordb

# 4. 构建 RAG 问答链
def create_qa_chain(vectordb):
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base="https://api.deepseek.com",
        temperature=0.7
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})  #减少返回块数（如从 3 改为 2），可减少发散来源。
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

# 5. 主交互函数
def ask_hu_tao(question):
    # 如果向量库已存在，直接加载；否则先构建
    if os.path.exists("./chroma_db"):
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com"
        )
        vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    else:
        docs = load_documents()
        chunks = split_documents(docs)
        vectordb = build_vectorstore(chunks)

    qa_chain = create_qa_chain(vectordb)
    result = qa_chain.invoke({"query": question})
    answer = result["result"]
    sources = [doc.metadata.get("source", "未知来源") for doc in result["source_documents"]]
    return answer, sources

if __name__ == "__main__":
    print("胡桃知识库问答系统启动（输入 quit 退出）")
    while True:
        q = input("你问：")
        if q.lower() in ("quit", "exit"):
            break
        ans, src = ask_hu_tao(q)
        print(f"胡桃：{ans}")
        print(f"（参考来源：{', '.join(set(src))}）")