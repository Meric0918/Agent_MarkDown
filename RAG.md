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

# 向量数据库

主流数据库：Pinecone、Milvus、**Chroma**、Faiss
## Chroma

- 功能丰富：支持查询、过滤、密度估计等多种功能

- 很多开发框架如LangChain都支持

- 相同的API可以在Python笔记本中运行，也可以扩展到集群，用于开发、测试和生产闭源

- 轻量级、易用性，易于集成和使用，特别适合小型或中型项目‌

- 开源
