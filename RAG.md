文档切分成chunk -> 文本向量化embedding -> 向量数据库
# 文档切分

1. 按照固定字符数切分
2. 按固定字符数，结合滑动窗口切分
3. 按照句子切分：根据。！？切分句子
4. 递归方法 RecursiveCharacterTextSplitter
	RecursiveCharacterTextSplitter 是一个用于将文本分割成较小块的工具。核心思想是根据一组分隔符（separators）逐步分割文本，直到每个块的大小都符合预设的chunk_size。如果某个块仍然过大，它会继续递归地分割，直到满足条件为止。其默认字符列表为 `["\n\n", "\n", " ", ""]`，这种设置首先尝试保持段落、句子和单词的完整性。
# 文本向量化

千问文本嵌入模型：text-embedding-v3
本地化部署：Ollama + bge-m3

# 向量相似度

1. 余弦距离 -- 越大越相似
2. 欧式距离 -- 越小越相似
