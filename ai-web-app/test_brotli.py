import requests
import brotli

url = 'https://www.baidu.com/s?wd=成都&pn=1&ie=utf-8'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

print(f"正在访问: {url}")
response = requests.get(url, headers=headers, timeout=10)

print(f"状态码: {response.status_code}")
print(f"内容长度: {len(response.text)}")
print(f"编码: {response.encoding}")
print(f"响应头 Content-Encoding: {response.headers.get('Content-Encoding', 'N/A')}")

if response.headers.get('Content-Encoding') == 'br':
    print("检测到Brotli压缩，尝试手动解压...")
    try:
        decompressed = brotli.decompress(response.content)
        print(f"解压后长度: {len(decompressed)}")
        html_content = decompressed.decode('utf-8')
        print(f"解压后文本长度: {len(html_content)}")
    except Exception as e:
        print(f"解压失败: {e}")
else:
    html_content = response.text
    print(f"文本长度: {len(html_content)}")

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
results = soup.select('div.result')
print(f"找到 {len(results)} 个搜索结果")
