文档切分成chunk -> 文本向量化embedding -> 向量数据库
# 文档切分

1. 按照固定字符数切分
2. 按固定字符数，结合滑动窗口切分
3. 按照句子切分：根据。！？切分句子
4. 递归方法 RecursiveCharacterTextSplitter
	RecursiveCharacterTextSplitter 是一个用于将文本分割成较小块的工具。核心思想是根据一组分隔符（separators）逐步分割文本，直到每个块的大小都符合预设的chunk_size。如果某个块仍然过大，它会继续递归地分割，直到满足条件为止。其默认字符列表为 `["\n\n", "\n", " ", ""]`，这种设置首先尝试保持段落、句子和单词的完整性。

```python
def extract_text_from_docx(filename, min_line_length=1):

    """

    从 DOCX 文件中提取文字

  

    思路：

    1. 使用 python-docx 库读取文档

    2. 提取所有段落的原始文本

    3. 按空行分割并重组段落

    4. 过滤短行（假设为标题）

    5. 处理英文连字符情况

  

    参数：

    filename: DOCX文件路径

    min_line_length: 最小行长度，短于此长度的行将被视为段落分隔符

  

    返回：

    段落列表（每个元素为一个段落字符串）

    """

    paragraphs = []

    buffer = ''

    full_text = ''

  

    # 读取文档

    doc = Document(filename)

  

    # 提取原始文本（保留换行符）

    for para in doc.paragraphs:

        full_text += para.text + '\n'

  

    # 处理文本内容

    lines = full_text.split('\n')

    for line in lines:

        # 有效行处理（长度超过阈值）

        if len(line) >= min_line_length:

            # 处理连字符情况

            if not line.endswith('-'):

                buffer += ' ' + line

            else:

                buffer += line.strip('-')

        # 遇到分隔行时存储段落

        elif buffer:

            paragraphs.append(buffer.strip())

            buffer = ''

  

    # 处理最后一个段落

    if buffer:

        paragraphs.append(buffer.strip())

  

    return paragraphs
```

```python
def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):

    """

    从 PDF 文件中（按指定页码）提取文字

  

    思路：

    1. 使用 pdfplumber 逐页解析 PDF

    2. 根据指定页码过滤需要处理的页面

    3. 提取页面中的文本容器（LTTextContainer）内容

    4. 将所有文本按行暂存后，重新合并被换行的段落

    5. 处理英文单词的连字符情况

    6. 按空行分割段落

  

    参数：

    filename: PDF文件路径

    page_numbers: 指定要提取的页码列表（从0开始），None表示提取全部

    min_line_length: 最小行长度，短于此长度的行将被视为段落分隔符

  

    返回：

    段落列表（每个元素为一个段落字符串）

    """

    paragraphs = []

    buffer = ''  # 用于暂存正在构建的段落

    full_text = ''  # 存储提取的原始文本

  

    # 提取全部文本

    for i, page_layout in enumerate(extract_pages(filename)):  # 遍历每一页

        # 过滤页码：如果指定了页码范围且当前页不在范围内，则跳过

        if page_numbers is not None and i not in page_numbers:

            continue

  

        # 遍历页面中的每个元素

        for element in page_layout:

            # 仅处理文本容器（排除图片、表格等元素）

            # 这个判断的作用是：只处理纯文本内容，跳过图片/表格/图形等非文本元素

            if isinstance(element, LTTextContainer):

                full_text += element.get_text() + '\n'  # 保留换行用于后续处理

  

    # 按空行分隔，重新组织段落

    lines = full_text.split('\n')

    for text in lines:

        # 处理有效行（长度超过阈值）

        if len(text) >= min_line_length:

            # 处理连字符情况：行以连字符结尾时，拼接时不加空格并去除连字符

            if not text.endswith('-'):

                buffer += ' ' + text  # 普通行拼接

            else:

                buffer += text.strip('-')  # 处理被换行分割的单词

        # 遇到空行时，将暂存内容作为段落存入列表

        elif buffer:

            paragraphs.append(buffer.strip())  # 去除首尾空格后存储

            buffer = ''  # 重置暂存区

  

    # 处理最后一个段落

    if buffer:

        paragraphs.append(buffer.strip())

  

    return paragraphs
```
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

将已有资料向量化存进向量知识库，然后将用户输入也向量化，使用向量相似度检索出对应内容
## 基于RAG实现公司HR制度智能问答系统
![](assets/RAG/file-20260212001848244.png)

# 混合检索

- 关键字检索：

检索速度快，如果用户输入的关键字能够准确地代表所需信息，且文本中该关键字的使用具有明确的指向性，那么可以得到较为准确的结果。但如果关键字具有歧义，或者文本中存在大量与关键字相关但语义不同的内容，可能会导致检索结果不准确，出现误判或漏判的情况。

- 全文检索：

通常比关键字检索更准确，因为它考虑了文本的整体内容和上下文信息。能够理解用户查询语句的语义，更精确地匹配相关文档，减少因关键字歧义或片面匹配导致的错误。不过，对于一些复杂的语义理解和模糊查询，全文检索可能也存在一定的局限性。

- 基于词向量的相似度检索：

在语义理解和准确匹配方面具有较大优势。大模型能够学习到文本中的深层语义信息，在处理复杂的语义查询和模糊匹配时表现较好，能够返回更符合用户意图的检索结果。

## 全文检索

BM25

```python
# 从 rank_bm25 库中导入 BM25Okapi 类，用于计算 BM25 相似度得分
from rank_bm25 import BM25Okapi  #  pip install rank_bm25
# 导入 jieba 库，用于中文分词
import jieba

# 定义一个包含多个文档的语料库，每个文档是一个字符串
# ['这‘，’是‘，第一个，。。。]
corpus = [
    "这是第一个文档",
    "这是第二个文档",
    "这是第三个文档"
]

# 对语料库中的每个文档进行分词操作，使用 jieba.lcut() 函数将文档分割成词语列表
# 最终得到一个包含多个词语列表的列表，每个子列表对应一个文档的分词结果
#  进行分词处理。

tokenized_corpus = [jieba.lcut(doc) for doc in corpus]
print(tokenized_corpus)

# 使用分词后的语料库初始化 BM25Okapi 对象，后续将使用该对象进行相似度计算
bm25 = BM25Okapi(tokenized_corpus)

# 定义一个查询语句，即要查找相关文档的关键词
query = "第一个文档"

# 对查询语句进行分词操作，将其转换为词语列表
tokenized_query = jieba.lcut(query)

# 调用 BM25Okapi 对象的 get_scores 方法，计算查询语句与语料库中每个文档的相似度得分

# 得到一个包含多个得分的列表，每个得分对应语料库中的一个文档
scores = bm25.get_scores(tokenized_query)

# 打印计算得到的相似度得分列表
print(scores)  # 输出示例：[ 0.39285845 -0.11796717 -0.11796717]

# 调用 BM25Okapi 对象的 get_top_n 方法，根据查询语句的相似度得分从语料库中选取前 n 个最相关的文档

# 这里 n 设置为 1，表示只选取最相关的一个文档
top_n = bm25.get_top_n(tokenized_query, corpus, n=1)

# 打印选取的最相关文档列表
print(top_n)  # 输出：['这是第一个文档']
```

区别：全文检索基于关键词的统计匹配，侧重精确性和可解释性；大模型相似度基于语义向量的空间距离，侧重语义理解和泛化能力。

## 医疗知识混合检索实战
![](assets/RAG/file-20260212002053901.png)
代码在assets中查看