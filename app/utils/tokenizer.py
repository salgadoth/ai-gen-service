from transformers import T5Tokenizer

def tokenize_input(text: str):
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    tokenized_input = tokenizer.encode(text, return_tensors="pt")
    return tokenized_input