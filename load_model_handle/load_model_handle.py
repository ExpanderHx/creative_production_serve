import gc

import torch
from transformers import AutoTokenizer, AutoModel


class LoadModelHandle(object):

    def __init__(self,model_config):
        self.model_config = model_config;

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained("D:\huggingface\THUDM--chatglm2-6b", trust_remote_code=True)
        model = AutoModel.from_pretrained("D:\huggingface\THUDM--chatglm2-6b", trust_remote_code=True).half().cuda()
        # self.tokenizer = AutoTokenizer.from_pretrained(self.model_config.tokenizer_name, trust_remote_code=True)
        # model = AutoModel.from_pretrained(self.model_config.model_name, trust_remote_code=True).half().cuda()
        self.model = model.eval()
        return self.model

    def close_model(self):
        if self.model is not None:
            self.model.close()
    def unload_model(self):
        del self.model
        del self.tokenizer
        self.model = self.tokenizer = None
        self.clear_torch_cache()

    def clear_torch_cache(self):
        gc.collect()
        if self.model_config is not None and self.model_config.load_device is not None and self.model_config.load_device.lower() != "cpu":
            if torch.has_mps:
                try:
                    from torch.mps import empty_cache
                    empty_cache()
                except Exception as e:
                    print(e)
                    print(
                        "如果您使用的是 macOS 建议将 pytorch 版本升级至 2.0.0 或更高版本，以支持及时清理 torch 产生的内存占用。")
            elif torch.has_cuda:
                device_id = "0" if torch.cuda.is_available() else None
                CUDA_DEVICE = f"{self.model_config.load_device}:{device_id}" if device_id else self.model_config.load_device
                with torch.cuda.device(CUDA_DEVICE):
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            else:
                print("未检测到 cuda 或 mps，暂不支持清理显存")

