import requests
from bs4 import BeautifulSoup

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
print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

# 检查响应头
print("\n=== 响应头 ===")
for key, value in response.headers.items():
    print(f"{key}: {value}")

# 尝试解码
print("\n=== 尝试解码HTML ===")
try:
    html_content = response.text
    print(f"解码成功，长度: {len(html_content)}")
    
    # 检查是否包含验证码
    if '验证码' in html_content:
        print("\n⚠️ 包含验证码页面")
    elif 'captcha' in html_content.lower():
        print("\n⚠️ 包含captcha")
    else:
        print("\n✓ 不包含验证码")
    
    # 检查是否包含搜索结果
    if '百度一下' in html_content:
        print("✓ 包含百度首页元素")
    if '百度为您找到' in html_content:
        print("✓ 包含搜索结果提示")
    
    # 保存HTML
    with open('baidu_test.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("\n已保存HTML到 baidu_test.html")
    
    # 显示前500个字符
    print("\n=== HTML前500个字符 ===")
    print(html_content[:500])
    
except Exception as e:
    print(f"解码失败: {str(e)}")
    import traceback
    traceback.print_exc()
