
# def execute_tool(tool_name, param=None):
#     """ 工具类型 """
#     tools = {
#         "roll_dice": roll_dice,
#         "get_current_time": get_current_time,
#         "calculate": calculate
#     }
#     if tool_name in tools:
#         if tool_name == "roll_dice":
#             result = roll_dice()
#             return f"摇骰子的结果：{result}"

#         elif tool_name == "get_current_time":
#             result = get_current_time()
#             return f"当前时间：{result}"

#         elif tool_name == "calculate":
#             if param is None:
#                 return "计算失败：没有提供表达式"
#             result = calculate(param)
#             return f"计算的结果：{result}"
#     else:
#         return "未知工具"


# def parse_tool_call(response_text):
#     """  工具名称捕捉  """
#     match = re.search(r'\[TOOL: (.*?)\]\s*(.*)$', response_text)
#     if match:
#         tool_name = match.group(1)
#         param = match.group(2)
#         return tool_name, param
#     else:
#         return None, None

def search_hu_tao(query, k=10, category=None):
    # 分类映射：关键词 -> 子目录名
    category_map = {
        "food": "食物喜好",
        "character": "角色评价",
        "story": "背景故事",
        "misc": "台词杂项",
    }
    
    sub_dir = category_map.get(category) if category else None
    
    # 加载对应目录的文档
    docs = load_documents(sub_dir)
    chunks = split_documents(docs)

# 索引路径按分类区分
    index_path = f"./faiss_index_{category}" if category else "./faiss_index"

    # 如果向量库已存在，直接加载；否则先构建
    if os.path.exists(index_path):
        vectordb = FAISS.load_local(
            index_path, 
            embedding_model,
            allow_dangerous_deserialization=True  # 因为是我们自己创建的，安全
        )
    else:
        print("【调试】开始检索")
        docs = load_documents()
        print(f"【调试】加载了 {len(docs)} 个文档")
        chunks = split_documents(docs)
        print(f"【调试】切分为 {len(chunks)} 个块")
        vectordb = build_vectorstore(chunks)
        print("【调试】FAISS 加载完成")

    # 构建 BM25 需要用到切分后的文档，所以这里必须重新加载并切分
    docs = load_documents()
    chunks = split_documents(docs)

    # 构建混合检索器
    ensemble_retriever = build_hybrid_retriever(chunks, vectordb)
    print("【调试】混合检索器构建完成")

    # 执行检索
    results = ensemble_retriever.invoke(query)
    print(f"【调试】检索到 {len(results)} 个结果")
    print("检索到的块：", [doc.page_content[:30] for doc in results])
    return [doc.page_content for doc in results[:k]]

