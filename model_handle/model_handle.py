import gc
from typing import List

import torch
from transformers.pipelines.text_generation import ReturnType

from chat.base import AnswerResult
from config.model_type_config import model_type_chatglm, model_type_llama
from load_model_handle.load_model_handle import LoadModelHandle
import xml.etree.ElementTree as ET

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
            if self.model_config.model_type is not None:
                if self.model_config.model_type == model_type_chatglm:
                    return self.generatorChatGlmAnswer(prompt, history, streaming);
                elif self.model_config.model_type == model_type_llama:
                    return self.generatorLLamaAnswer(prompt,history,streaming);
                else:
                    pass
            else:
                if "chatglm" in self.model_config.model_name :
                    return self.generatorChatGlmAnswer(prompt,history,streaming);
                elif "lama" in self.model_config.model_name:
                    return self.generatorLLamaAnswer(prompt,history,streaming);
                else:
                    return self.generatorLLamaAnswer(prompt, history, streaming);




    def generatorLLamaAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False):
        inputList = [];
        # promptIntegration = f'<s>Human: {prompt}\n</s><s>Assistant: '
        promptIntegration = prompt
        if history is not None:
            history = history[(-(len(history)+1) if self.model_config.history_len > len(history) else (
                -self.model_config.history_len)):-1] if (self.model_config.history_len > 0 and len(history) > 0) else []
            for historyItem in history:
                if historyItem is not None and len(historyItem)>1:
                    pass
                    # inputList.append(f'<s>Human: {historyItem[0]}\n</s><s>Assistant: {historyItem[1]}</s>');
        inputList.append(promptIntegration);
        model_inputs = self.load_model_handle.tokenizer([promptIntegration], return_tensors="pt",add_special_tokens=False,padding=False);
        input_ids = model_inputs.input_ids
        if torch.cuda.is_available() and (
                self.load_model_handle.model_config.load_device is None or self.load_model_handle.model_config.load_device != "cpu"):
            input_ids = input_ids.to('cuda')
        prompt_length = len(
            self.load_model_handle.tokenizer.decode(
                input_ids[0],
                skip_special_tokens=True,
            )
        )
        generate_input = {
            "input_ids": input_ids,
            "attention_mask":model_inputs.attention_mask,
        }
        self.set_generation_config();
        generate_ids = self.load_model_handle.model.generate(**generate_input)
        text = self.load_model_handle.tokenizer.decode(
            generate_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        try:

            all_text = text[prompt_length:]
            # if all_text is None:
            #     text = text.replace(promptIntegration, '')
            #
            #     text_list = text.split("</s>");
            #     if text_list is not None:
            #         if len(text_list) > 1 and text_list[1] is not None and len(text_list[1]) > 0:
            #             text = text_list[1].split("<s>")[1].replace('Assistant:', '')
            #         else:
            #             text_list = text_list[0].split("<s>")
            #             if text_list is not None:
            #                 if len(text_list) > 1 and text_list[1] is not None and len(text_list[1]) > 0:
            #                     text = text_list[1].replace('Assistant:', '')
            #                 else:
            #                     text = text_list[0].replace('Assistant:', '')
            text = all_text
            try:
                root_element_tree = ET.fromstring(text)
                if root_element_tree is not None and len(root_element_tree) > 1:
                    text = root_element_tree[1].text
            except:
                pass
                # print("root_element_tree LLama text 处理异常")
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


    def set_generation_config(self):
        try:
            if self.load_model_handle.model.generation_config is not None:
                self.load_model_handle.model.generation_config.max_new_tokens = self.load_model_handle.model_config.max_token;
                self.load_model_handle.model.generation_config.do_sample = True;
                self.load_model_handle.model.generation_config.top_k = 50;
                self.load_model_handle.model.generation_config.top_p = self.load_model_handle.model_config.top_p;
                self.load_model_handle.model.generation_config.temperature = self.load_model_handle.model_config.temperature;
                self.load_model_handle.model.generation_config.repetition_penalty = 1.3;
                self.load_model_handle.model.generation_config.eos_token_id = self.load_model_handle.model_config.eos_token_id;
                self.load_model_handle.model.generation_config.bos_token_id = self.load_model_handle.model_config.bos_token_id;
                self.load_model_handle.model.generation_config.pad_token_id = self.load_model_handle.model_config.pad_token_id;
        except:
            pass


    def clear_torch_cache(self):
        gc.collect()
        if hasattr(self, 'llm_device'):
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



