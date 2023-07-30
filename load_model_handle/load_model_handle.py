import gc
import os

import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM, AutoConfig

from config.model_type_config import model_type_chatglm, model_type_llama


class LoadModelHandle(object):

    def __init__(self,model_config):
        self.model = None
        self.tokenizer = None
        self.model_config = model_config;

    def load_model(self):
        # self.tokenizer = AutoTokenizer.from_pretrained("D:\huggingface\THUDM--chatglm2-6b", trust_remote_code=True)
        # model = AutoModel.from_pretrained("D:\huggingface\THUDM--chatglm2-6b", trust_remote_code=True).half().cuda()

        model_name = self.model_config.model_name
        model_path = self.model_config.model_path
        if model_path is not None and len(model_path.strip()) > 0:
            model_name = model_path;

        if model_name is not None:
            # model_name = model_name.replace('\\\\', '/')
            model_name = model_name.replace('\\', '/')
            # path = os.path.join(os.path.realpath(model_name));
            path = model_name;
            autoConfig = AutoConfig.from_pretrained(path, trust_remote_code=True)
            print(autoConfig)
            if autoConfig is not None:
                print(autoConfig.model_type);
                self.model_config.autoConfig = autoConfig
                self.model_config.model_type = autoConfig.model_type;
                if autoConfig.model_type == model_type_chatglm:
                    return self.load_model_glm();
                elif autoConfig.model_type == model_type_llama:
                    return self.load_model_llama();
                else:
                    return self.load_more_type_model();

        model_name = self.model_config.model_name
        if model_name is not None:
            if "chatglm" in model_name :
                return self.load_model_glm();
            elif "lama" in model_name:
                return self.load_model_llama();
            else:
                return self.load_more_type_model();


    def load_model_glm(self):
        tokenizer_name = self.model_config.tokenizer_name
        model_name = self.model_config.model_name
        model_path = self.model_config.model_path
        if model_path is not None and len(model_path.strip()) > 0:
            tokenizer_name = model_path;
            model_name = model_path;

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, trust_remote_code=True)
        if torch.cuda.is_available() and (
                self.model_config.load_device is None or self.model_config.load_device != "cpu"):
            model = self.load_model_gpu_handle(AutoModel.from_pretrained(model_name, trust_remote_code=True))
        else:
            model = AutoModel.from_pretrained(model_name, trust_remote_code=True).float()
        self.model = model.eval()
        return self.model

    def load_model_llama(self):
        tokenizer_name = self.model_config.tokenizer_name
        model_name = self.model_config.model_name
        model_path = self.model_config.model_path
        if model_path is not None and len(model_path.strip()) > 0:
            tokenizer_name = model_path;
            model_name = model_path;

        config = AutoConfig.from_pretrained(tokenizer_name);
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if config is not None:
            self.tokenizer.pad_token_id = config.pad_token_id
        if torch.cuda.is_available() and (
                self.model_config.load_device is None or self.model_config.load_device != "cpu"):
            #  device_map='auto',torch_dtype=torch.float16,load_in_8bit=True
            # print(torch.get_default_dtype())
            # torch.set_default_dtype(torch.float16);
            model = self.load_model_gpu_handle(AutoModelForCausalLM.from_pretrained(model_name));
        else:
            # , device_map='auto',torch_dtype=torch.float16,load_in_8bit=True
            model = AutoModelForCausalLM.from_pretrained(model_name)
            try:
                pass
                # model = model.float()
            except Exception:
                print("当前模型不支持half")
        self.model = model.eval()
        return self.model

    def load_more_type_model(self):
        tokenizer_name = self.model_config.tokenizer_name
        model_name = self.model_config.model_name
        model_path = self.model_config.model_path
        if model_path is not None and len(model_path.strip()) > 0:
            tokenizer_name = model_path;
            model_name = model_path;

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, trust_remote_code=True)
        if torch.cuda.is_available() and (
                self.model_config.load_device is None or self.model_config.load_device != "cpu"):

            model = self.load_model_gpu_handle(AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True))
        else:
            model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).float()
        self.model = model.eval()
        return self.model

    # def _get_model_class(self,autoConfig):
    #     if autoConfig is not None:
    #         if hasattr(autoConfig,'architectures'):
    #             if autoConfig.architectures is not None and  len(autoConfig.architectures) > 0:
    #                 architecture = autoConfig.architectures[0]



    def load_model_gpu_handle(self, model):
        if model is not None:
            if self.model_config.is_half:
                try:
                    model = model.half();
                except Exception:
                    print("当前模型不支持half")
        return model.cuda()

    def close_model(self):
        if self.model is not None:
            self.model.close()
    def unload_model(self):
        if 'model' in dir(self):
            del self.model
        if 'tokenizer' in dir(self):
            del self.tokenizer
        self.model = self.tokenizer = None
        self.clear_torch_cache()

    def clear_torch_cache(self):
        gc.collect()
        if self.model_config is not None and self.model_config.load_device is not None and self.model_config.load_device.lower() != "cpu" and torch.cuda.is_available() :
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

