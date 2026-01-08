import requests
from bs4 import BeautifulSoup
import json
import gzip
import io

url = "https://www.baidu.com/s"
params = {
    'wd': '人工智能',
    'pn': 0,
    'ie': 'utf-8'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

print("正在请求百度搜索...")
response = requests.get(url, params=params, headers=headers, timeout=10)

print(f"状态码: {response.status_code}")
print(f"实际URL: {response.url}")
print(f"内容长度: {len(response.content)}")

# requests会自动解压gzip，所以直接使用response.text
html_content = response.text

# 保存HTML
with open('baidu_search_debug.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("已保存HTML到 baidu_search_debug.html")

# 检查是否是验证码页面
if '验证码' in html_content or 'captcha' in response.url.lower():
    print("\n⚠️ 遇到验证码页面，无法继续爬取")
    print("这是百度的反爬虫机制")
else:
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有可能的结果容器
    print("\n=== 查找搜索结果容器 ===")

    # 方法1: 查找class包含result的div
    results1 = soup.find_all('div', class_=lambda x: x and 'result' in str(x).lower())
    print(f"方法1 (class包含'result'): {len(results1)} 个")

    # 方法2: 查找class包含c-container的div
    results2 = soup.find_all('div', class_=lambda x: x and 'c-container' in str(x))
    print(f"方法2 (class包含'c-container'): {len(results2)} 个")

    # 方法3: 查找所有h3标签
    h3_tags = soup.find_all('h3')
    print(f"方法3 (h3标签): {len(h3_tags)} 个")

    # 方法4: 查找所有包含链接的div
    divs_with_a = soup.find_all('div', class_=lambda x: x and x)
    divs_with_links = [d for d in divs_with_a if d.find('a')]
    print(f"方法4 (包含链接的div): {len(divs_with_links)} 个")

    # 显示前5个h3标签
    if h3_tags:
        print("\n=== 前5个h3标签 ===")
        for i, h3 in enumerate(h3_tags[:5]):
            print(f"\n{i+1}. {h3.get_text(strip=True)[:100]}")
            a_tag = h3.find('a')
            if a_tag:
                print(f"   链接: {a_tag.get('href', 'N/A')[:100]}")

    # 显示前3个result div
    if results1:
        print("\n=== 前3个result div ===")
        for i, div in enumerate(results1[:3]):
            print(f"\n{i+1}. {str(div)[:200]}...")

    # 显示前3个c-container div
    if results2:
        print("\n=== 前3个c-container div ===")
        for i, div in enumerate(results2[:3]):
            print(f"\n{i+1}. {str(div)[:200]}...")

    # 尝试查找所有div的class
    print("\n=== 所有div的class属性 ===")
    all_divs = soup.find_all('div')
    classes = set()
    for div in all_divs[:50]:
        if div.get('class'):
            classes.add(' '.join(div.get('class')))
    
    print(f"找到 {len(classes)} 个不同的class:")
    for cls in sorted(list(classes))[:20]:
        print(f"  - {cls}")
