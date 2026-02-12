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
-  ...

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
- XMLOutputParser

## Chain

```python
# prompt -> client -> parser
chain = chat_template | client | parser

# 传参需要是字典，key要和模版中的变量名一致

print(chain.invoke({"language":"法语", "text":"你好，今天的天真蓝"}))
```