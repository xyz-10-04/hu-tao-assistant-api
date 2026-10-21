# 胡桃助手 (Hu Tao Assistant) - 基于 RAG 与 ReAct Agent 的角色问答系统

## 📖 项目简介
基于混合检索（BM25 + 向量检索）与 ReAct Agent 架构的原神角色问答系统。项目脱离了纯框架依赖，从零手写了 BM25 与 RRF 融合算法，并通过自建评测集完成了 RAG 链路的量化调优。

## 🛠 技术栈
- **核心语言**：Python 3.14
- **大模型 API**：DeepSeek API (通过 langchain-openai 接入)
- **检索与向量**：FAISS, BGE-small-zh (Embedding)
- **Web 框架**：FastAPI, Streamlit
- **数据库**：SQLite, SQLAlchemy (用于持久化记忆)

## ✨ 核心亮点
1. **手写底层算法**：脱离 LangChain 封装，纯手写中文分词（基于 jieba）、BM25 打分、以及 RRF（倒数排名融合）算法，深刻理解检索底层原理。
2. **混合检索策略**：结合 BM25（关键词精准匹配）与 BGE（语义向量泛化），通过 RRF 算法加权融合，大幅提升召回率。
3. **数据驱动的调优**：建立 20 条标准评测集（涵盖人物设定、故事背景、角色评价），Recall@3 达到 95%。
4. **Agent 智能路由**：基于 ReAct 模式，大模型自主判断是否需要调用工具，支持混合检索、计算、时间查询及长期记忆保存。

## 🏗 系统架构流程
1. 用户提问通过 FastAPI/Streamlit 传入后端。
2. Agent（大模型）接收 Prompt 与工具列表，判断是否需要调用工具。
3. 若需要检索，Agent 调用 `search_hu_tao_knowledge` 工具。
4. 检索器并行执行：
   - BM25 进行关键词倒排检索。
   - FAISS 进行 BGE 向量语义检索。
   - 使用 RRF 算法对两路结果进行重新排序。
5. 检索结果与用户问题拼接，交回大模型进行最终回答生成（若一次未解决，ReAct 循环会继续，设有最大步数限制）。

## 🕳 踩坑与优化记录 (V1.0 -> V3.0)
- **Embedding 模型的演进**：初版使用 `chinese-roberta-wwm-ext-large` 直接生成向量，发现完全不具备语义检索能力（问“喜欢吃什么”召回“烦恼”）。通过消融实验确认后，替换为专为检索优化的 `BGE-small-zh`，纯 FAISS 的 Top-1 准确率显著提升。
- **切分策略的调优**：
  - 初始 `chunk_size=250`：切分过大，导致一条 chunk 混入多条不相干台词，检索命中率虚高但噪音极大。
  - 调整 `chunk_size=150`：统一切分导致长故事文本被腰斩，短台词失去上下文，Recall@3 跌至 30%。
  - **最终方案**：在 `split_documents` 中引入定制策略。针对短文本（台词/评价）按 `\n\n` 严格切分，保证单句独立；针对长文本（角色故事）采用 `chunk_size=300, overlap=50`，保证上下文连贯。最终 Recall@3 达到 95%。

## 🚀 快速复现指南
### 1. 环境准备
```bash
# 创建虚拟环境并激活
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install -r requirements.txt

# 启动 Agent 控制台对话
python main.py
# 启动后端 API
uvicorn main_api:app --reload
```