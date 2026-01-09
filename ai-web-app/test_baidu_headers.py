import requests
from bs4 import BeautifulSoup

url = 'https://www.baidu.com/s?wd=成都&pn=1&ie=utf-8'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.baidu.com/',
}

print(f"正在访问: {url}")
session = requests.Session()
response = session.get(url, headers=headers, timeout=10)

print(f"状态码: {response.status_code}")
print(f"内容长度: {len(response.text)}")
print(f"编码: {response.encoding}")
print(f"响应头 Content-Encoding: {response.headers.get('Content-Encoding', 'N/A')}")
print(f"最终URL: {response.url}")

print(f"\n前500个字符:")
print(response.text[:500])

soup = BeautifulSoup(response.text, 'html.parser')
results = soup.select('div.result')
print(f"\n找到 {len(results)} 个搜索结果")

# 尝试其他选择器
other_selectors = [
    'div[class*="result"]',
    'div.c-container',
    'div[tpl]',
    'div[data-log]',
]

for selector in other_selectors:
    count = len(soup.select(selector))
    print(f"选择器 '{selector}': 找到 {count} 个元素")
