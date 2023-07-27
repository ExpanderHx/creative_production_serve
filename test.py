# from transformers import AutoModelForCausalLM
#
# model = AutoModelForCausalLM.from_pretrained("fnlp/moss-moon-003-sft")
import os
import time

import torch
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
import pathlib
# path = pathlib.Path('E:\build\models\chatglm2-6b')
# autoConfig = AutoConfig.from_pretrained("E:\build\models\chatglm2-6b", trust_remote_code=True)


# path = os.path.join(os.path.realpath("E:\\build\\models\\chatglm2-6b"));
# autoConfig = AutoConfig.from_pretrained(path, trust_remote_code=True)
# print(autoConfig)

path = os.path.join(os.path.realpath("E:\\build\\creative_production_win_gpu\\models\\Llama-2-7b-chat-hf"));
autoConfig = AutoConfig.from_pretrained(path, trust_remote_code=True)
print(autoConfig)

if autoConfig is not None :
    print(autoConfig.model_type);
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