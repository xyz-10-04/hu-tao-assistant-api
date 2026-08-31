RAG 集成到 Agent 调试记录
项目：胡桃助手（Hu Tao Assistant）
日期：2026-08-30
目标：将 RAG 知识库作为 LangChain Tool 集成到 Agent 中，使 Agent 能自动检索并回答关于胡桃的背景故事、角色关系等问题。

一、问题与解决记录
1. 循环导入导致 FastAPI 启动失败
现象：

执行 uvicorn main_api:app --reload 后终端报错：

text
ImportError: cannot import name 'agent' from 'langchain_main'
前端报错：

text
无法连接到后端服务：HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /chat
原因：
导入链形成了循环依赖：

text
main_api.py → langchain_main.py → langchain_tools.py → rag_build.py → api.py → langchain_main.py
其中 api.py 中存在一条未被使用的导入语句 from langchain_main import agent，导致闭环。

解决方案：
在 api.py 中注释掉 from langchain_main import agent。

验证：
重启 FastAPI 服务，启动成功，无导入错误。

2. Hugging Face 模型下载网络超时
现象：

FastAPI 启动后卡在模型下载阶段，反复重试：

text
[WinError 10060] 连接尝试失败 Retrying in Xs [Retry X/5]
原因：

rag_build.py 中的 sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 模型需从 Hugging Face 下载。

国内网络无法直接访问 Hugging Face，导致下载超时。

解决方案：
在启动 FastAPI 前设置环境变量，使用国内镜像源：

powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
uvicorn main_api:app --reload
模型从镜像源成功下载，服务正常启动。

验证：
模型下载完成，服务启动成功，前端可正常连接。

3. RAG 工具测试通过
测试目标：验证 Agent 能否自动调用 RAG 工具并返回准确回答。

测试用例：

用户输入	预期行为	实际结果
“你认识钟离吗”	Agent 调用 RAG，返回钟离与胡桃的关系信息	✅ 回答准确，包含“往生堂客卿、博学多才、常忘带摩拉”等细节
“胡桃的生日是哪天”	Agent 调用 RAG，返回生日信息	✅ 回答准确，包含“7月15日”及相关描述
验证结论：
两个问题均正确命中知识库，回答内容准确，语气符合胡桃人设。

二、当前状态总结
检查项	状态
FastAPI 服务正常启动	✅
无循环导入报错	✅
Hugging Face 模型已下载到本地缓存	✅
RAG 工具已封装并注册到 Agent	✅
Agent 能自动路由到 RAG	✅
知识库检索结果准确	✅
回答风格自然	✅
三、文件修改记录
文件	修改内容	目的
api.py	注释掉 from langchain_main import agent	消除循环导入
rag_build.py	保留 search 函数，删除 ask 函数及无关导入	简化 RAG 模块，避免循环依赖
langchain_tools.py	新增 retrieve_hu_tao_knowledge 工具	封装 RAG 检索功能供 Agent 调用
四、后续优化建议
高优先级
扩充知识库内容：增加更多关于胡桃的故事、台词、人际关系等文本块，丰富知识库。

优化工具描述：如果后续发现 Agent 不调用 RAG 的情况，调整工具描述中的关键词，提高路由准确率。

中优先级
调整检索参数：根据使用情况优化 k 值和相似度阈值，提升检索精确度。

模型下载缓存：当前模型已下载到本地缓存，后续无需联网即可运行。

低优先级
知识库自动更新：考虑实现增量更新机制，新知识可实时入库。

多知识库路由：后续可扩展为根据问题类型路由到不同知识库。

五、附录：测试截图说明
注：已通过两个 RAG 用例测试：

“你认识钟离吗” → 命中角色关系知识，回答包含“往生堂客卿、常忘带摩拉”等细节。

“胡桃的生日是哪天” → 命中事实性知识，回答包含“7月15日”。