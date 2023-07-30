# from transformers import AutoModelForCausalLM
#
# model = AutoModelForCausalLM.from_pretrained("fnlp/moss-moon-003-sft")
import os
import time

import torch
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, AutoModel
import pathlib

import xml.etree.ElementTree as ET


text = """
<s>Human: 你好
</s>
<s>Assistant: 我是 Assistant，很高兴为您提供服务。有什么需要我的吗？</s>
"""

# root_element_tree = ET.fromstring(text)
#
# print(root_element_tree)

# Use a pipeline as a high-level helper
from transformers import pipeline
# pipe = pipeline("text-generation", model="lmsys/vicuna-7b-v1.3")
pipe = pipeline("text-generation", model="E:\\build\\creative_production_win_gpu\\models\\Llama-2-7b-chat-hf")
returnData = pipe("你好")
print(returnData)

# a = {"a":1,"b":1}
# b = {"b":2}
#
# b = {**a,**b}
# print(b)


# path = pathlib.Path('E:\build\models\chatglm2-6b')
# autoConfig = AutoConfig.from_pretrained("E:\build\models\chatglm2-6b", trust_remote_code=True)


# path = os.path.join(os.path.realpath("E:\\build\\models\\chatglm2-6b"));
# autoConfig = AutoConfig.from_pretrained(path, trust_remote_code=True)
# print(autoConfig)

# path = os.path.join(os.path.realpath("E:\\build\\creative_production_win_gpu\\models\\Llama-2-7b-chat-hf"));
# path = "lmsys/vicuna-7b-v1.3"
# path = os.path.join(os.path.realpath("E:\\build\\creative_production_win_gpu\\models\\Llama-2-7b-chat-hf"));
# autoConfig = AutoConfig.from_pretrained(path, trust_remote_code=True)
# print(autoConfig)
#
#
#
# if autoConfig is not None :
#     print(autoConfig.model_type);
#
# # autoModel = AutoModel.from_pretrained(path, trust_remote_code=True).half().cuda()
# autoModelForCausalLM = AutoModelForCausalLM.from_pretrained(path, trust_remote_code=True).half().cuda()
#
# autoTokenizer = AutoTokenizer.from_pretrained(path);
#
# input_ids = autoTokenizer(["<s>Human: 你好\n</s><s>Assistant: "], return_tensors="pt",
#                               add_special_tokens=False).input_ids.to('cuda')
# generate_input = {
#     "input_ids": input_ids,
#     "max_new_tokens": 200,
#     "do_sample": True,
#     "top_k": 50,
#     "top_p": 3,
#     "temperature":0.7,
#     "repetition_penalty": 1.3,
#     "eos_token_id": autoTokenizer.eos_token_id,
#     "bos_token_id": autoTokenizer.bos_token_id,
#     "pad_token_id": autoTokenizer.pad_token_id
# }
# # generate_ids = autoModel.generate(**generate_input)
# generate_ids = autoModelForCausalLM.generate(**generate_input)
# text = autoTokenizer.decode(generate_ids[0])
#
# print(text);
# print("------------")

# print(torch.cuda.is_available())
# print(torch.cuda.device_count())
# print(torch.cuda.get_device_name(0))


# a = snapshot_download(repo_id="fnlp/moss-moon-003-sft")
# a = snapshot_download(repo_id="fnlp/moss-moon-003-sft-plugin-int8")
# a = snapshot_download(repo_id="THUDM/chatglm-6b-int4")
# a = snapshot_download(repo_id="THUDM/chatglm-6b-int8")

while True:
    try:
        # a = snapshot_download(repo_id="THUDM/chatglm-6b")
        # a = snapshot_download(repo_id="THUDM/chatglm2-6b")
        # a = snapshot_download(repo_id="THUDM/chatglm-6b-int4")
        # a = snapshot_download(repo_id="vicuna-7b-v1.3")

        # tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        # model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        # model.chat();
        break
    except Exception:
        print("网络异常,准备重试")
        time.sleep(3)
#
#
# print(a)