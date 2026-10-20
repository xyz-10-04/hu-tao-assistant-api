from modelscope import snapshot_download

# 这行代码的意思是：下载模型，并保存在当前目录下的 "models" 文件夹里
model_dir = snapshot_download('BAAI/bge-small-zh-v1.5', cache_dir='./models')
print(f"模型下载完成，路径是: {model_dir}")