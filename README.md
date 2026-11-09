# 胡桃助手 (Hu Tao Assistant) - 基于 RAG 与 ReAct Agent 的角色问答系统

## 📖 项目简介
基于混合检索（BM25 + 向量检索）与 ReAct Agent 架构的原神角色问答系统。项目脱离了纯框架依赖，从零手写了 BM25、RRF 融合算法以及安全的 AST 求值器，并引入了 BGE-Reranker 精排，通过自建评测集完成了 RAG 链路的量化调优。

## 🛠 技术栈
- **核心语言**：Python 3.10+
- **大模型 API**：DeepSeek API (通过 langchain-openai 接入)
- **检索与向量**：手写 BM25、RRF、FAISS、BGE-small-zh (Embedding)、BGE-Reranker (精排)
- **Web 与安全**：FastAPI, Streamlit, AST (安全求值)
- **数据库**：SQLite, SQLAlchemy (用于持久化记忆)

## ✨ 核心亮点
1. **手写底层算法**：脱离 LangChain 封装，纯手写中文分词、BM25 打分以及 RRF 融合算法，深刻理解检索底层原理。
2. **三级检索漏斗**：结合 BM25 与 BGE 向量粗排召回，通过 RRF 融合，最后利用 BGE-Reranker (Cross-Encoder) 进行二次精排，大幅提升上下文质量。
3. **数据驱动的调优**：建立 20 条标准评测集（涵盖人物设定、故事背景、角色评价），经过定制化切分与模型替换，**Recall@3 达到 100%**（已排除答案映射错误）。
4. **Agent 智能路由与安全**：基于 ReAct 模式自主调用工具；彻底废弃不安全的 `eval()`，基于 `ast` 模块手写安全求值器，杜绝代码注入与 DoS 风险。

## 🏗 系统架构流程
1. 用户提问通过 FastAPI/Streamlit 传入后端。
2. Agent 接收 Prompt 与工具列表，判断是否需要调用工具。
3. 若需要检索，Agent 调用 `search_hu_tao_knowledge` 工具。
4. 检索器并行执行：
   - BM25 进行关键词倒排检索。
   - FAISS 进行 BGE 向量语义检索。
   - 使用 RRF 算法对两路结果进行融合（粗排）。
   - 使用 BGE-Reranker 对 Top-N 候选集重新打分排序（精排）。
5. 检索结果与用户问题拼接，交回大模型生成最终回答（ReAct 循环设有最大步数限制）。

## 🕳 踩坑与优化记录 (V1.0 -> V3.0)
1. **Embedding 模型的演进**：初版使用 `chinese-roberta` 直接生成向量，发现完全不具备语义检索能力。通过消融实验确认后，替换为专为检索优化的 `BGE-small-zh`。
2. **切分策略的调优**：
   - 初始 `chunk_size=250`：切分过大，混入多条无关台词，噪音极大。
   - 调整 `chunk_size=150`：统一切分导致长故事文本腰斩，Recall@3 跌至 30%。
   - **最终方案**：引入定制策略。短文本（台词/评价）按 `\n\n` 严格切分；长文本（故事）采用 `chunk_size=300, overlap=50`。
3. **精排模型的引入**：发现长实体问题（如“钟离客卿”）无法命中 Top-3，引入 `bge-reranker-base` 进行二次精排，将 Recall@1 从 85% 提升至 90%，**Recall@3 达到 100%**。
4. **计算器工具的漏洞**：早期采用 `eval()` 配合白名单，存在 `9**9**9` 的 DoS 攻击风险。后重构为基于 `ast` 的安全求值器，拦截了所有非四则运算节点，保障运行稳定。

## 🚀 快速复现指南
### 1. 环境准备
```bash
# 创建虚拟环境并激活
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install -r requirements.txt
```

### 2. 模型与环境变量
```bash
下载本地模型：请先运行 python download_model.py 下载 BGE 向量模型和 Reranker 模型至本地 models/ 目录。

配置 API Key：在根目录创建 .env 文件，配置 DEEPSEEK_API_KEY=sk-xxxxxx。
```

### 3. 启动服务
```bash
# 启动 Agent 控制台对话 (CLI)
python main.py

# 启动后端 API 
uvicorn main_api:app --reload

# 启动前端 Web 界面
streamlit run app.py
```