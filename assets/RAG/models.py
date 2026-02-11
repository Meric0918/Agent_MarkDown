# \RAG\models.py
#可用模型列表，以及获得访问模型的客户端
ALI_TONGYI_API_KEY_SYSVAR_NAME = "DASHSCOPE_API_KEY"
ALI_TONGYI_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ALI_TONGYI_MAX_MODEL = "qwen-max-latest"
ALI_TONGYI_DEEPSEEK_R1 = "deepseek-r1"
ALI_TONGYI_DEEPSEEK_V3 = "deepseek-v3"
ALI_TONGYI_REASONER_MODEL = "qvq-max-latest"
ALI_TONGYI_EMBEDDING = "text-embedding-v3"
ALI_TONGYI_RERANK = "gte-rerank-v2"

DEEPSEEK_API_KEY_SYSVAR_NAME = "Deepseek_Key"
DEEPSEEK_URL = "https://api.deepseek.com/v1"
DEEPSEEK_CHAT_MODEL = "deepseek-chat"
DEEPSEEK_REASONER_MODEL = "deepseek-reasoner"



#当前实际使用的模型
from enum import Enum
class Constants(Enum):
    API_KEY_SYSVAR_NAME = ALI_TONGYI_API_KEY_SYSVAR_NAME
    BASE_URL = ALI_TONGYI_URL
    LLM_MODEL = ALI_TONGYI_MAX_MODEL
    EMBEDDING_MODEL = ALI_TONGYI_EMBEDDING
    RERANK_MODEL = ALI_TONGYI_RERANK
    REASONER_MODEL = ALI_TONGYI_DEEPSEEK_R1

import os
from langchain_openai import ChatOpenAI
from openai import OpenAI
import inspect

#通过LangChain获得指定平台和模型的客户端，缺省平台和模型来自Constants中的常量
def get_lc_model_client(api_key=os.getenv(Constants.API_KEY_SYSVAR_NAME.value), base_url=Constants.BASE_URL.value
                        , model=Constants.LLM_MODEL.value, verbose=False, debug=False):
    function_name = inspect.currentframe().f_code.co_name
    if(verbose):
        print(f"{function_name}:{base_url},{model}")
    if(debug):
        print(f"{function_name}:{base_url},{model},{api_key}")
    return ChatOpenAI(api_key=api_key, base_url=base_url,model=model)

#获得指定平台的客户端，但未指定具体模型，缺省平台来自Constants中的常量
def get_normal_client(api_key=os.getenv(Constants.API_KEY_SYSVAR_NAME.value), base_url=Constants.BASE_URL.value,
                      verbose=False, debug=False):
    function_name = inspect.currentframe().f_code.co_name
    if(verbose):
        print(f"{function_name}:{base_url}")
    if(debug):
        print(f"{function_name}:{base_url},{api_key}")
    return OpenAI(api_key=api_key, base_url=base_url)