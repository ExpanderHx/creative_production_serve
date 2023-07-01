

class ModelConfig(object):

    def __init__(self):
        self.model_name = None;
        self.model_path = None;
        self.tokenizer_name = None;
        self.load_device = None;
        self.history_len = 10;
        self.max_token = 1000;
        self.temperature = 0.01;
        self.top_p = 0.9;


    @classmethod
    def handle_dict(cls, dataDict):
        obj = cls()
        for attr, val in dataDict.items():
            setattr(obj, attr, val)
        if obj.tokenizer_name is None:
            obj.tokenizer_name = obj.model_name;
        if obj.load_device is None:
            obj.load_device = "cuda";
        return obj