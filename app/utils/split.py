import nltk

def split_into_sentences(text: str):
    return nltk.sent_tokenize(text)