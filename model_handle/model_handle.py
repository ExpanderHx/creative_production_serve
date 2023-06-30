import gc
from typing import List

import torch

from chat.base import AnswerResult
from load_model_handle.load_model_handle import LoadModelHandle


class ModelHandle(object):

    def __init__(self,model_config):
        self.model_config = model_config
        self.load_model_handle = LoadModelHandle(model_config)

    def load_model(self):
        self.model = self.load_model_handle.load_model()

    def reload_model(self,model_config):
        self.unload_model();
        if model_config is not None:
            self.model_config = model_config
            self.load_model_handle.model_config = model_config;
        self.model = self.load_model_handle.load_model()

    def unload_model(self):
        if self.load_model_handle is not None:
            self.model = None
            self.load_model_handle.unload_model();


    def generatorAnswer(self, prompt: str,
                         history: List[List[str]] = [],
                         streaming: bool = False):

        if streaming:
            history += [[]]
            for inum, (stream_resp, _) in enumerate(self.load_model_handle.model.stream_chat(
                    self.load_model_handle.tokenizer,
                    prompt,
                    history=history[-self.model_config.history_len:-1] if ( self.model_config.history_len > 0 and len(history) >0 ) else [],
                    max_length=self.model_config.max_token,
                    temperature=self.model_config.temperature
            )):
                history[-1] = [prompt, stream_resp]
                answer_result = AnswerResult()
                answer_result.history = history
                answer_result.llm_output = {"answer": stream_resp}
                yield answer_result
        else:
            response, _ = self.model.chat(
                self.load_model_handle.tokenizer,
                prompt,
                history=history[-self.model_config.history_len:] if ( self.model_config.history_len > 0 and len(history) >0 ) else [],
                max_length=self.model_config.max_token,
                temperature=self.model_config.temperature
            )
            self.clear_torch_cache()
            history += [[prompt, response]]
            answer_result = AnswerResult()
            answer_result.history = history
            answer_result.llm_output = {"answer": response}
            yield answer_result


    def clear_torch_cache(self):
        gc.collect()
        if self.llm_device.lower() != "cpu":
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
                CUDA_DEVICE = f"{self.llm_device}:{device_id}" if device_id else self.llm_device
                with torch.cuda.device(CUDA_DEVICE):
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            else:
                print("未检测到 cuda 或 mps，暂不支持清理显存")



