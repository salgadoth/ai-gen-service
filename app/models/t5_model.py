from transformers import T5ForConditionalGeneration, T5Tokenizer

class T5Model:
    def __init__(self, model_path="t5-small"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)

    def infer(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors='pt', padding=True, truncation=True)
        outputs = self.model.generate(**inputs)
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text