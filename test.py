from rag_build import search_hu_tao
# 这个不传 category，会触发全库检索，如果 ./faiss_index 不存在，它会自己建
print(search_hu_tao("胡桃喜欢吃什么", k=3))