# from transformers import AutoModelForCausalLM
#
# model = AutoModelForCausalLM.from_pretrained("fnlp/moss-moon-003-sft")
import time

from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

# a = snapshot_download(repo_id="fnlp/moss-moon-003-sft")
# a = snapshot_download(repo_id="fnlp/moss-moon-003-sft-plugin-int8")
# a = snapshot_download(repo_id="THUDM/chatglm-6b-int4")
# a = snapshot_download(repo_id="THUDM/chatglm-6b-int8")
while True:
    try:
        # a = snapshot_download(repo_id="THUDM/chatglm-6b")
        # a = snapshot_download(repo_id="THUDM/chatglm2-6b")
        # a = snapshot_download(repo_id="THUDM/chatglm-6b-int4")
        a = snapshot_download(repo_id="meta-llama/Llama-2-7b-chat-hf")

        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        # model.chat();
        break
    except Exception:
        print("网络异常,准备重试")
        time.sleep(3)


print(a)