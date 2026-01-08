from openai import OpenAI
import os
from app.config import Config

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def analyze_sentiment(self, text):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情分析助手，请分析以下文本的情感倾向。"},
                    {"role": "user", "content": text}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def classify_topic(self, text):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文本分类助手，请对以下文本进行主题分类。"},
                    {"role": "user", "content": text}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"分类失败: {str(e)}"
    
    def extract_entities(self, text):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的实体识别助手，请从以下文本中提取关键实体（人名、地名、机构名等）。"},
                    {"role": "user", "content": text}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"实体提取失败: {str(e)}"
