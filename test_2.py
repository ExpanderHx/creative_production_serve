# from transformers import AutoModelForCausalLM
#
# model = AutoModelForCausalLM.from_pretrained("fnlp/moss-moon-003-sft")
import os
import time

import torch
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, AutoModel
import pathlib


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
        a = snapshot_download(repo_id="lmsys/vicuna-7b-v1.3")


        break
    except Exception:
        print("网络异常,准备重试")
        time.sleep(3)
#
#
print(a)