# 实现了一个混合搜索系统，结合了BM25和密集向量检索两种方法
#pip install rank_bm25
#pip install jieba
import numpy as np
from rank_bm25 import BM25Okapi
import jieba
import json
import chromadb
from chromadb.config import Settings

from models import get_normal_client, Constants
get_normal_client(debug=True)
# 查询的问题
query = "得了白癜风，怎么办"

# 1、读取文件准备处理
with open('train_zh.json', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

# 记录数太多，只取10条数据
# instruction->症状描述；output->症状解释或治疗方案
instructions = [entry['instruction'] for entry in data[0:25]]
# print(instructions[0])
outputs = [entry['output'] for entry in data[0:25]]
# print(outputs[0])

#---------------------------------------------------------
#2、开始BM25进行全文检索
#在运用 BM25 算法进行全文检索时，需要对文档进行分词，以此把文本拆分成一个个独立的词语，方便后续计算词语在文档中的频率等统计信息
# 文档分词 jieba.lcut(doc)  函数会把 instructions 列表里的每个文档 doc 进行分词
tokenized_corpus = [jieba.lcut(doc) for doc in instructions]
print(tokenized_corpus)

# 初始化一个BM25Okapi对象，用于基于BM25算法的文本检索或相似度计算
#对传入的文档计算必要的统计信息
bm25 = BM25Okapi(tokenized_corpus)

# 问题分词 :对查询的问题也需要进行分词处理，这样才能计算查询词和文档的相似度分数。
tokenized_query = jieba.lcut(query)

# 通过BM25算法计算查询词与文档的相似度分数
bm25_scores = bm25.get_scores(tokenized_query)
# 通过BM25算法获取与查询最相关的前3个结果
bm25_results = bm25.get_top_n(tokenized_query, outputs, n=3)
print("BM25 Score: ", bm25_scores)
print("BM25 Results: ", bm25_results)
#
# #---------------------------------------------------------
# #3、开始词向量相似度检索
client = get_normal_client()
#
# #封装向量模型与API的交互操作，通过自定义函数 get_embeddings 提供向量模型的调用。
def get_embeddings(texts, model=Constants.EMBEDDING_MODEL.value):
    data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]
# #封装与向量数据库（ChromaDB）的交互操作，通过自定义类 MyVectorDBConnector 提供添加文档和检索文档的功能。
# # 具体步骤包括初始化数据库客户端、创建集合、添加文档及其对应的向量表示，以及根据查询向量检索相似文档。
class MyVectorDBConnector:
    # collection_name：向量数据库中集合的名称。embedding_fn：一个用于将文本转换为向量的函数。
    def __init__(self, collection_name, embedding_fn):
        # 初始化 ChromaDB 客户端 并重置数据库
        chroma_client = chromadb.Client(Settings(allow_reset=True))
        # 重置数据库，这一步主要用于演示，实际使用中通常不需要每次都重置
        chroma_client.reset()

        # 创建一个 集合 collection 在向量数据库中，集合是存储向量数据以及相关元数据的容器
        #get_or_create_collection 方法用于获取或创建一个集合，如果集合不存在则创建一个新集合。
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        # 定义一个函数，用于将文本转换为向量表示，并返回一个包含向量表示的列表。
        self.embedding_fn = embedding_fn

    # 添加文档与向量
    def add_documents(self, instructions, outputs):
        '''向 collection 中添加文档与向量'''
        # get_embeddings(instructions)  #  对问题进行向量化，
        embeddings = self.embedding_fn(instructions)
        # 向 collection 中添加文档与向量
        self.collection.add(
            embeddings=embeddings,  # 每个文档的向量
            documents=outputs,  # 文档的原文
            ids=[f"id{i}" for i in range(len(instructions))]  # 每个文档的 id
        )

        # print(self.collection.count())
    # 定义检索函数， 在向量数据库里进行检索操作
    def search(self, query, top_n):
        '''检索向量数据库'''
        # self.collection.query() 这是 ChromaDB 集合对象的一个方法，用于在集合中执行查询操作。
        results = self.collection.query(
            #  query_embeddings是查询文本的向量表示
            # 调用在类初始化时传入的嵌入函数 self.embedding_fn，把查询文本 query 转换为向量。
            # 要注意的是，self.embedding_fn 期望接收一个字符串列表作为输入，所以这里把 query 放在列表 [query] 里。
            query_embeddings=self.embedding_fn([query]),
            # 指定要返回的最相似文档的数量。
            n_results=top_n
        )
        # 返回检索结果  results 是一个字典，其中包含了和查询向量最相似的 top_n 个文档的相关信息，像文档的原文、向量、ID 等。
        return results
#
#
# 创建一个向量数据库对象
vector_db = MyVectorDBConnector("demo", get_embeddings)

# 向向量数据库中添加文档
vector_db.add_documents(instructions, outputs)
# 根据问题进行检索，返回最相似的 top_n 个结果
results = vector_db.search(query, 3)
# 打印最相似的 top_n 个结果
print("vector_db:", results['documents'][0])
#

# #
# # #---------------------------------------------------------
# 4、组合BM25和词向量相似度检索的结果

# 对BM25和密集检索的分数进行标准化处理
# 标准化处理是将数据转换到统一的区间范围内(如[0,1])的过程
# 这样可以消除不同度量标准带来的影响,使不同特征之间具有可比性 ，相似度分数
# 使用 np.array() 函数把 bm25_scores 转换为 NumPy 数组。
# bm25_scores 原本可能是 Python 列表，转换为 NumPy 数组后，能更方便地进行数值计算，因为 NumPy 提供了很多高效的数组操作函数。
bm25_scores = np.array(bm25_scores)
# BM25分数标准化到[0,1]区间
#用数组中的每个元素除以最大值，实现将分数缩放到 [0, 1] 区间的目的。
# 例如，若最大值是 10，那么所有分数都会除以 10，使得最大值变为 1，其他分数也会相应缩小。
bm25_scores_normalized = bm25_scores / np.max(bm25_scores)

query_embedding = np.array(get_embeddings(query))  # 获取查询的向量表示，并把结果转换为 NumPy 数组
doc_embeddings = np.array(get_embeddings(instructions))  # 获取文档的向量表示，并把结果转换为 NumPy 数组
# 计算查询向量和文档向量之间的欧氏距离
# np.linalg.norm 函数用于计算向量的范数，这里计算的是向量差的 L2 范数，即欧氏距离。axis=1 表示按行计算。
dense_scores = np.linalg.norm(query_embedding - doc_embeddings, axis=1)
# 将距离转换为相似度分数并标准化到[0,1]区间
# 将欧氏距离转换为相似度分数，并将其标准化到 [0, 1] 区间。欧氏距离越小，相似度越高，所以用 1 减去标准化后的距离得到相似度分数。
dense_scores_normalized = 1 - (dense_scores / np.max(dense_scores))


# 3. 将两种方法的分数进行加权组合
# bm25_scores_normalized 是之前计算得到的 BM25 分数的标准化结果。
# dense_scores_normalized 是向量相似度分数的标准化结果。
# 权重均为 0.5。这样可以综合考虑两种方法的优点，得到更准确的文档相关性评分。
combined_scores = 0.5 * bm25_scores_normalized + 0.5 * bm25_scores_normalized
#[0.00078102 0.6844611  0.11295923 0.13353093 0.10878262 0.00591407
 # 0.         0.11458926 0.10642415 0.12681826]
print(combined_scores)
# print(0.7 * vector_scores_normalized1)
# 4. 根据组合分数对结果排序并返回前3个最相关的文档
#对 combined_scores 数组中的值进行降序排序，并返回排序后的索引值
# argsort() 高到低进行排序0.6844611。。。0.  返回数据的索引值 # [::-1]切片 方向
top_idx = combined_scores.argsort()[::-1]
# top_idx = combined_scores
print(top_idx) # [1 3 9 7 2 4 8 5 0 6]
print(combined_scores.argsort())
hybrid_results = [outputs[i] for i in top_idx[:3]] # 1 3 9

# 5. 输出混合搜索的结果
print("Hybrid Search Results: ", hybrid_results)

