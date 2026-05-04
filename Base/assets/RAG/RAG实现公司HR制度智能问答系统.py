#RAG实现公司HR制度智能问答系统.py
#需要
#pip install python-docx
#pip install pdfminer.six
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import chromadb
from chromadb.config import Settings
from docx import Document

from models import get_normal_client, Constants

client = get_normal_client()

# 读取PDF文本内容的函数，供参考，本示例中没有用到
def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):
    '''从 PDF 文件中（按指定页码）提取文字'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # 提取全部文本
    for i, page_layout in enumerate(extract_pages(filename)):
        # 如果指定了页码范围，跳过范围外的页
        if page_numbers is not None and i not in page_numbers:
            continue
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                full_text += element.get_text() + '\n'

    # 按空行分隔，将文本重新组织成段落
    lines = full_text.split('\n')
    for text in lines:
        if len(text) >= min_line_length:
            buffer += (' ' + text) if not text.endswith('-') else text.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs

# 读取Word文档
def extract_text_from_docx(filename, min_line_length=1):
    '''从 DOCX 文件中提取文字'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # 打开并读取文档
    doc = Document(filename)
    # 提取全部文本
    for para in doc.paragraphs:
        full_text += para.text + '\n'

    # 按空行分隔，将文本重新组织成段落
    lines = full_text.split('\n')
    for line in lines:
        # 这里其实起到一个分块的作用，原文中的标题往往字数小于10个，
        #如果当前行的长度小于10，认为是标题，不加到paragraphs中进行后续处理
        #这里的分块是比较粗糙的
        if len(line) >= min_line_length:
            buffer += (' ' + line) if not line.endswith('-') else line.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs

# 使用示例
docx_filename = "D:\\Agent\\03_RAG\\07-RAG认知与项目实战 （二）-25.5.16\\1.rag认知与项目实战\\基于RAG实现公司HR制度智能问答系统\\人事管理流程.docx"
# 读取Word文件
paragraphs = extract_text_from_docx(docx_filename, min_line_length=10)

# paragraphs = extract_text_from_pdf("人事管理流程.pdf", page_numbers=[
#                                    2, 3], min_line_length=10)

# 向量数据库类
class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        chroma_client = chromadb.Client(Settings(allow_reset=True))
        # 为了演示，实际不需要每次 reset()
        # chroma_client.reset()

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        batch_size = 10
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            self.collection.add(
                embeddings=self.embedding_fn(batch_docs),  # 每个文档的向量
                documents=batch_docs,  # 文档的原文
                ids=[f"id{i}" for i in range(i, i + len(batch_docs))]  # 每个文档的 id
            )

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results

# 使用千问的模型进行向量化
def get_embeddings(texts, model=Constants.EMBEDDING_MODEL.value):
    data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]

# 创建一个向量数据库对象
vector_db = MyVectorDBConnector("demo", get_embeddings)

# 向向量数据库中添加文档1
vector_db.add_documents(paragraphs)

# llm模型
def get_completion(prompt, model=Constants.LLM_MODEL.value):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""

# 给Prompt 模板赋值
def build_prompt(prompt_template, **kwargs):
    '''将 Prompt 模板赋值'''
    prompt = prompt_template
    for k, v in kwargs.items():
        if isinstance(v, str):
            val = v
        elif isinstance(v, list) and all(isinstance(elem, str) for elem in v):
            val = '\n'.join(v)
        else:
            val = str(v)
            # 返回转换为大写的字符串副本
        prompt = prompt.replace(f"__{k.upper()}__", val)
    return prompt

# 定义 chat 函数
def rag_chat(vector_db,llm_api,user_query,n_results=2):
    # 1.检索
    search_results = vector_db.search(user_query, n_results)
    # 2.构建提示词模板build_prompt
    prompt =  build_prompt(prompt_template,info=search_results['documents'][0],query=user_query)
    # 3,调用LLM模型方法生成回答
    response=llm_api(prompt)
    return response

user_query =  '视为不符合录用条件的情形有哪些？'
response =  rag_chat(vector_db,get_completion,user_query)
print(response)