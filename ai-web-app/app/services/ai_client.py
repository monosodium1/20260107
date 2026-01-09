import requests
import json


class AIClient:
    """AI模型客户端，支持OpenAI API范式"""

    def __init__(self, api_url, api_key, model_name, system_prompt=None):
        """
        初始化AI客户端

        Args:
            api_url: API地址
            api_key: API密钥
            model_name: 模型名称
            system_prompt: 系统提示词
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt or "你是一个智能助手，请根据用户的问题提供准确、有用的回答。"
        
        # 检查URL是否已经包含完整路径
        if not self.api_url.endswith('/chat/completions'):
            self.chat_endpoint = f'{self.api_url}/chat/completions'
        else:
            self.chat_endpoint = self.api_url

    def chat(self, messages, temperature=0.7, max_tokens=2000, timeout=120):
        """
        聊天对话

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            timeout: 超时时间（秒），默认120秒

        Returns:
            dict: 包含响应和token使用情况的字典
        """
        if not messages:
            return {
                'success': False,
                'error': '消息不能为空'
            }

        if self.system_prompt:
            messages.insert(0, {
                'role': 'system',
                'content': self.system_prompt
            })

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model_name,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        try:
            print(f"正在请求API: {self.chat_endpoint}")
            print(f"模型名称: {self.model_name}")
            print(f"超时设置: {timeout}秒")
            print(f"请求数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            response = requests.post(
                self.chat_endpoint,
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                choices = result.get('choices', [])
                if not choices:
                    return {
                        'success': False,
                        'error': '未收到有效响应'
                    }

                message = choices[0].get('message', {})
                content = message.get('content', '')
                
                usage = result.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)

                return {
                    'success': True,
                    'content': content,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'finish_reason': choices[0].get('finish_reason', 'stop')
                }
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', error_msg)
                except:
                    pass
                
                return {
                    'success': False,
                    'error': f'API请求失败: {error_msg}',
                    'status_code': response.status_code
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '请求超时，请稍后重试'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知错误: {str(e)}'
            }

    def test_connection(self):
        """
        测试连接

        Returns:
            dict: 测试结果
        """
        test_messages = [
            {
                'role': 'user',
                'content': '你好，请简单介绍一下你自己。'
            }
        ]

        result = self.chat(test_messages, max_tokens=100)
        
        if result['success']:
            return {
                'success': True,
                'message': '连接成功',
                'response': result['content'],
                'tokens_used': result['total_tokens']
            }
        else:
            return {
                'success': False,
                'message': result['error']
            }
