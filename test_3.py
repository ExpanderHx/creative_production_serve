# from transformers import AutoModelForCausalLM
#
# model = AutoModelForCausalLM.from_pretrained("fnlp/moss-moon-003-sft")
# import os
# import time
#
# import torch
# from huggingface_hub import snapshot_download
# from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, AutoModel
# import pathlib
#
# import xml.etree.ElementTree as ET

#
# from modelscope.pipelines import pipeline
# from modelscope.utils.constant import Tasks
#
# p = pipeline('portrait-matting', 'damo/cv_unet_image-matting')
# a= p('D:\\downloads\\微信图片_20230725044952_1.jpg',)
# print(a)


# text = """
# <s>Human: 你好
# </s>
# <s>Assistant: 我是 Assistant，很高兴为您提供服务。有什么需要我的吗？</s>
# """

# root_element_tree = ET.fromstring(text)
#
# print(root_element_tree)

# Use a pipeline as a high-level helper
# from transformers import pipeline
# # pipe = pipeline("text-generation", model="lmsys/vicuna-7b-v1.3")
# pipe = pipeline("text-generation", model="E:\\build\\models\\Llama-2-7b-chat-hf")
# returnData = pipe("你好")
# print(returnData)

# a = {"a":1,"b":1}
# b = {"b":2}
#
# b = {**a,**b}
# print(b)

