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
        self.model = None
        if 'load_model_handle' in dir(self):
            self.load_model_handle.unload_model();

    def generatorAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False):

        if self.model_config is not None:
            if "chatglm" in self.model_config.model_name :
                return self.generatorChatGlmAnswer(prompt,history,streaming);
            elif "lama" in self.model_config.model_name:
                return self.generatorLLamaAnswer(prompt,history,streaming);




    def generatorLLamaAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False):
        promptIntegration = f'<s>Human: {prompt}\n</s><s>Assistant: '
        input_ids = self.load_model_handle.tokenizer([promptIntegration], return_tensors="pt",
                              add_special_tokens=False).input_ids.to('cuda')
        generate_input = {
            "input_ids": input_ids,
            "max_new_tokens": self.load_model_handle.model_config.max_token,
            "do_sample": True,
            "top_k": 50,
            "top_p": self.load_model_handle.model_config.top_p,
            "temperature": self.load_model_handle.model_config.temperature,
            "repetition_penalty": 1.3,
            "eos_token_id": self.load_model_handle.tokenizer.eos_token_id,
            "bos_token_id": self.load_model_handle.tokenizer.bos_token_id,
            "pad_token_id": self.load_model_handle.tokenizer.pad_token_id
        }
        generate_ids = self.load_model_handle.model.generate(**generate_input)
        text = self.load_model_handle.tokenizer.decode(generate_ids[0])

        try:
            text = text.replace(promptIntegration, '')
            text = text.split("</s>")[1].split("<s>")[1].replace('Assistant:','')
        except:
            print("LLama text 处理异常")



        # self.clear_torch_cache()
        history += [[prompt, text]]
        answer_result = AnswerResult()
        answer_result.history = history
        answer_result.llm_output = {"answer": text}
        yield answer_result

    def generatorChatGlmAnswer(self, prompt: str,
                         history: List[List[str]] = [],
                         streaming: bool = False):

        if streaming:
            history += [[]]
            for inum, (stream_resp, _) in enumerate(self.load_model_handle.model.stream_chat(
                    self.load_model_handle.tokenizer,
                    prompt,
                    history=history[(-(len(history)) if self.model_config.history_len > len(history)else (-self.model_config.history_len)):-1] if ( self.model_config.history_len > 0 and len(history) >0 ) else [],
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
                history=history[(-(len(history)) if self.model_config.history_len > len(history)else (-self.model_config.history_len)):-1] if ( self.model_config.history_len > 0 and len(history) >0 ) else [],
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



