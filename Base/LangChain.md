# 介绍
LangChain是一个用于开发由LLMs驱动的应用程序的框架。
![](assets/LangChain/file-20260212153728197.png)

## Model I/O

1. 提示词模板
2. 语言模型
3. 输出解析

## 提示词模板

- PromptTemplate
```python
template_str = "您是一位专业的程序员。\n对于信息 {text} 进行简短描述"
fact_text = "langchain"

# 第一种形式
prompt = PromptTemplate.from_template(template_str)

#第二种形式，有明显的约束，要求使用该模版时，必给变量 {text} 赋值
prompt2 =PromptTemplate(

    input_variables=["text"],

    template=template_str

)
print(prompt.format(text=fact_text))
```
- ChatPromptTemplate
```python
#聊天模版

#接收聊天消息/聊天消息列表

#消息分角色:系统消息，用户消息，助手消息(大模型的应答消息)

chat_template = ChatPromptTemplate.from_messages(

    [

        #用SystemMessagePromptTemplate来实现可以

        ('system',"请将以下的内容翻译成{language}"),

        HumanMessagePromptTemplate.from_template("{text}")

        #('human',"{text}"),

    ]

)

print(client.invoke(chat_template.format(language="英文", text="你好，今天的天真蓝")))

print(client.invoke(chat_template.format(language="法文", text="你好，今天的天真蓝")))
```
- FewShotPromptTemplate

-  提示模板部分格式化：适用于需要先给某些参数赋值，其余参数后期赋值。
```python

def get_datetime():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 配置一个提示模板
prompt_tmplt_txt = "讲一个关于{date}的{story_type}"

prompt = PromptTemplate(
    template=prompt_tmplt_txt,
    input_variables=["date", "story_type"]
)

half_p = prompt.partial(date=get_datetime())
#....其他业务代码
half_p.format(story_type="笑话")
half_p.format(story_type="悲伤的故事")
```

## 输出解析器（OutputParser）

- StrOutputParser
```python
# 原始输出
result = client.invoke(chat_template.format(language="英文", text="你好，今天的天真蓝"))

#字符串输出解析器
parser = StrOutputParser()

print(parser.invoke(result))
```

- DateOutputParser
- JsonOutputParser
使用Json输出解析器需要配合提示词进行，确保输出以Json格式返回
- XMLOutputParser

## Chain

```python
# prompt -> client -> parser
chain = chat_template | client | parser

# 传参需要是字典，key要和模版中的变量名一致

print(chain.invoke({"language":"法语", "text":"你好，今天的天真蓝"}))
```

**注意**：开启LangChain应用程序的调试功能

```python
#开启调试模型

langchain.debug = True
```
## LangServer

```python
#部署为服务

app = FastAPI(title="基于LangChain的大模型应用",version="V1.5",description="翻译服务")

add_routes(app, chain, path="/tslServer")

  

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
    

'''比如在postman或者apifox中访问http://localhost:8000/tslServer/invoke

在body中选择json，然后输入

{

    "input":

    {

        "language":"意大利文",

        "text":"为了部落！"

    }

}'''
```
## LCEL

LangChain Expression language，用一种用声明式的方法来链接LangChain组件

- RunnableLambda()可以将自定义函数变成链中的一个组件，或者可以使用@chain在函数上标记注解
- RunnableParrallel / RunnableMap()
```python
def add_one(x: int) -> int:

    return x + 1

  

def mul_two(x: int) -> int:

    return x * 2

  

def mul_three(x: int) -> int:

    return x * 3

  

#组件化

runnable_1 = RunnableLambda(add_one)

runnable_2 = RunnableLambda(mul_two)

runnable_3 = RunnableLambda(mul_three)

  

#串行

chain_seq = runnable_1 | runnable_2 | runnable_3

print(chain_seq.invoke(1))

  

#并行

chain2 = runnable_1 | RunnableParallel(

    mul_two=runnable_2,

    mul_three=runnable_3)

  

print(chain2.invoke(1))
# 输出为字典 {'mul_two': 4, 'mul_three': 6}
```
- RunnablePassthrough
```python
# RunnablePassthrough原样进行数据传递

runnable = RunnableParallel(

    passed=RunnablePassthrough(),

    modified=lambda x: x["num"] + 1,

)

print(runnable.invoke({"num": 1}))  
# {'passed': {'num': 1}, 'modified': 2}


# RunnablePassthrough对数据增强后传递

runnable = RunnableParallel(

    passed=RunnablePassthrough().assign(query=lambda x: x["num"] + 2),

    modified=lambda x: x["num"] + 1,

)

print(runnable.invoke({"num": 1})) 
# {'passed': {'num': 1, 'query': 3}, 'modified': 2}
```
## ChatMessageHistory

专门的消息历史组件
```python
chat_template = ChatPromptTemplate.from_messages(

    [

        SystemMessagePromptTemplate.from_template("你是人工智能助手"),

        #历史消息的存放地

        MessagesPlaceholder(variable_name="messages")

        #('placeholder',"{messages}")

    ]

)

  

client = get_lc_model_client()

  

parser = StrOutputParser()

chain =  chat_template | client | parser

  

chat_history = ChatMessageHistory()

chat_history.add_user_message('你好，我是云帆')

response = chain.invoke({'messages':chat_history.messages})

print(response)

#把大模型响应加入历史消息

chat_history.add_ai_message(response)

print(chat_history.messages)

chat_history.add_user_message('你好，我是谁？')

print(chain.invoke({'messages': chat_history.messages}))
```
## RunnableWithMessageHistory

自动会话历史管理组件RunnableWithMessageHistory
```python
#定义提示模版
prompt_template = ChatPromptTemplate.from_messages(

    [

        SystemMessagePromptTemplate.from_template("你是一个聊天助手，用{language}回答所有的问题"),

        #表示需要把以前的聊天记录作为对话内容的一部分发给大模型

        MessagesPlaceholder(variable_name="history"),

        ("human", "{input}"),

    ]

)

  

parser = StrOutputParser()

# 以链的形式

chain = prompt_template | client | parser

  

#有一个东西，保存所有用户的所有聊天记录

store={}

  

#根据每个用户自己的session_id，去获取这个用户的聊天记录

'''这里我们是将用户的会话历史保存在本机内存中，在实际业务中一般会保存到Redis缓存,

代码一般如下所示，注意代码未经测试，只做示范：

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

def get_redis_history(session_id: str) -> BaseChatMessageHistory:

    return RedisChatMessageHistory(session_id, redis_url=REDIS_URL)'''

def get_session(session_id:str):

    if session_id not in store:

        store[session_id] = ChatMessageHistory()

    return store[session_id]

  

chatbot_with_his = RunnableWithMessageHistory(

    chain,

    get_session,

    input_messages_key="input",

    history_messages_key="history"

)

  

#从业务角度来说，每个的Session_id遵循某种算法

config_chn = {'configurable':{'session_id':"yunfang_chinese"}}

config_eng = {'configurable':{'session_id':"yunfang_english"}}

  

resp = chatbot_with_his.invoke(

    {

        "input": [HumanMessage(content="你好，我是云帆。")],

        "language": "中文"

    },

    config = config_chn

)

print(resp)

  

resp = chatbot_with_his.invoke(

    {

        "input": [HumanMessage(content="你好，我是云帆。")],

        "language": "英文"

    },

    config = config_eng

)

print(resp)

  

resp = chatbot_with_his.invoke(

    {

        "input": [HumanMessage(content="请问我的名字是什么？")],

        "language": "中文"

    },

    config = config_chn

)

  

print(resp)

  

resp = chatbot_with_his.invoke(

    {

        "input": [HumanMessage(content="请问我的名字是什么？")],

        "language": "英文"

    },

    config = config_eng

)

print(resp)
```

## 查看流程

chain.get_graaph().print_ascii()

## 流式输出

invoke换成stream

## 文档切割器

- CharacterTextSplitter，基于字符(默认为"\n\n")进行切割
- RecursiveCharacterTextSplitter，支持对特定的编程语言(‘JavaScript’、‘cpp’、‘go’、‘java’ 、‘php’、‘python’等等)的代码进行切割
- MarkdownHeaderTextSplitter，可以根据指定的一组标题来切割一个Markdown 文档。