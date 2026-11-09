from modelscope import snapshot_download

# 把之前的 bge-small-zh-v1.5 改成 bge-reranker-base
model_dir = snapshot_download('BAAI/bge-reranker-base', cache_dir='./models')
print(f"模型下载完成，路径是: {model_dir}")
