# 介绍
LangChain是一个用于开发由LLMs驱动的应用程序的框架。
![](assets/LangChain/file-20260212153728197.png)

## Model I/O

1. 提示词模板
2. 语言模型
3. 输出解析

## 提示词模板

1. PromptTemplate
```python
template_str = "您是一位专业的程序员。\n对于信息 {text} 进行简短描述"
fact_text = "langchain"

prompt = PromptTemplate.from_template(template_str)
print(prompt.format(text=fact_text))
```
2. ChatPromptTemplate
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
1. FewShotPromptTemplate