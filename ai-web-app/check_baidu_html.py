#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查百度搜索页面结构
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.baidu.com/s"
params = {"wd": "人工智能", "ie": "utf-8"}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, params=params, headers=headers)
print(f"状态码: {response.status_code}")
print(f"URL: {response.url}")
print(f"\n页面内容长度: {len(response.text)}")

soup = BeautifulSoup(response.text, 'html.parser')

# 查找搜索结果容器
print("\n=== 查找搜索结果 ===")

# 方法1: 查找所有包含结果的div
results = soup.find_all('div', class_=lambda x: x and 'result' in x.lower())
print(f"\n方法1: 找到 {len(results)} 个包含'result'的div")

# 方法2: 查找所有c-container
results = soup.find_all('div', class_='c-container')
print(f"方法2: 找到 {len(results)} 个c-container")

# 方法3: 查找所有包含h3的div
results = soup.find_all('div', class_=lambda x: x and 'c-container' in str(x))
print(f"方法3: 找到 {len(results)} 个包含c-container的div")

# 显示前3个结果
print("\n=== 前3个搜索结果 ===")
for i, result in enumerate(results[:3]):
    print(f"\n结果 {i+1}:")
    print(f"  HTML: {str(result)[:200]}...")
    
    # 尝试提取标题
    title = result.find('h3')
    if title:
        print(f"  标题: {title.get_text(strip=True)[:100]}")
    
    # 尝试提取链接
    link = result.find('a')
    if link:
        print(f"  链接: {link.get('href', 'N/A')[:100]}")
    
    # 尝试提取摘要
    abstract = result.find(class_=lambda x: x and 'abstract' in str(x).lower())
    if abstract:
        print(f"  摘要: {abstract.get_text(strip=True)[:100]}")

# 保存HTML到文件用于分析
with open('baidu_search.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n\n已保存HTML到 baidu_search.html")
