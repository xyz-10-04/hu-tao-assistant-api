import os
from modelscope import snapshot_download
from pathlib import Path

# 设置你想要的模型本地存放目录，比如项目根目录下的 models
base_dir = Path("./models")
base_dir.mkdir(exist_ok=True)

for model_id in ['BAAI/bge-small-zh-v1.5', 'BAAI/bge-reranker-base']:
    # 提取出模型的名字，比如 bge-small-zh-v1.5
    model_name = model_id.split('/')[-1]
    target_dir = base_dir / model_name
    
    path = snapshot_download(model_id, local_dir=target_dir)
    print(f"{model_id} 下载完成，保存在 -> {path}")