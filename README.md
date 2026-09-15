# 胡桃助手 (Hu Tao Assistant)

一个基于 RAG 与 ReAct Agent 的角色问答 AI 助手。  
用胡桃的第一人称语气，回答关于《原神》角色胡桃的设定、故事、人际关系，同时支持基础工具调用与长期记忆。

## ✨ 功能亮点

- **角色知识问答（RAG）**  
  基于本地知识库检索，准确回答胡桃的生日、武器、故事、对其他角色的评价等。  
  混合检索：**BM25 + FAISS 向量检索**，按“食物喜好 / 角色评价 / 背景故事”分类建索引，避免多类别互相挤占。  
  经过调优，角色识别召回率从 **20% 提升至 90%**（测试集 30 个问题）。

- **Agent 工具调用**  
  基于 **LangChain ReAct Agent**，模型自主决策调用以下工具：  
  `roll_dice`、`get_current_time`、`calculate`、`save_note`、`read_notes`、`search_food_knowledge`、`search_character_knowledge`、`search_story_knowledge`。

- **长期记忆**  
  用 **SQLite + SQLAlchemy** 持久化存储用户姓名、偏好，通过工具 `save_user_info` / `query_user_info` 存取。  
  下次对话时，胡桃能记住你的名字。

- **流式输出**  
  后端 **FastAPI + SSE**，前端 **Streamlit** 逐字显示，聊天体验更自然。

- **工程化**  
  模块化拆分、环境变量管理、日志轮转、依赖精简（100+ → 20 个）。

## 🧠 技术栈

| 模块 | 技术 |
|------|------|
| AI 框架 | LangChain, FAISS, sentence-transformers |
| Embedding 模型 | `chinese-roberta-wwm-ext-large` |
| 大语言模型 | DeepSeek API |
| 后端 | FastAPI, SQLAlchemy, SQLite |
| 前端 | Streamlit |
| 工具链 | Git, Python, python-dotenv |

## 📁 项目结构
```
hu-tao-assistant-api/
├── knowledge/ # 胡桃知识库（按类别分子目录）
│ ├── 食物喜好/
│ ├── 角色评价/
│ ├── 背景故事/
│ └── 台词杂项/
├── faiss_index_*/ # 各分类的 FAISS 索引（自动生成）
├── app.py # Streamlit 前端
├── main_api.py # FastAPI 后端入口
├── langchain_main.py # Agent 初始化与系统提示词
├── langchain_tools.py # LangChain @tool 工具定义
├── rag_build.py # RAG 检索逻辑（混合检索 + 分类路由）
├── memory.py # 记忆读写（SQLAlchemy）
├── models.py # 数据库模型
├── database.py # 数据库连接
├── config.py # 配置常量
├── archive/ # 旧版本代码（命令行版）
├── requirements.txt
└── README.md
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/xyz-10-04/hu-tao-assistant-api.git
cd hu-tao-assistant-api
```

### 2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 3. 配置环境变量
在项目根目录创建 .env 文件，填入：
```
DEEPSEEK_API_KEY=你的DeepSeek密钥
```

### 4. 准备 Embedding 模型
```
项目依赖本地模型 chinese-roberta-wwm-ext-large，需提前下载到 bert/chinese-roberta-wwm-ext-large/，并在 rag_build.py 中修改 model_name 路径。如需自行下载，可使用 Hugging Face 或镜像站 https://hf-mirror.com。
```

### 5. 启动后端
```bash
uvicorn main_api:app --reload
```

### 6. 启动前端
另开一个终端：
```bash
streamlit run app.py
```

浏览器打开 http://localhost:8501 即可与胡桃对话。


🧪 测试与效果
测试集：30 个预设问题（角色设定、生日、武器、食物、人际关系等）
准确率：≥90%（人工判断答案是否引用文档原文）
优化措施：混合检索、分类索引、Prompt 工程、工具拆分、chunk_size=90、k=8

📌 后续计划
增量更新知识库
支持多轮对话上下文
扩展更多角色知识库
```