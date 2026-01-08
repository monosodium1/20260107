import jieba
import jieba.analyse

def extract_keywords(text, top_k=10):
    keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
    return [{'keyword': k, 'weight': w} for k, w in keywords]

def segment_text(text):
    return list(jieba.cut(text))

def clean_text(text):
    import re
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    text = text.strip()
    return text
