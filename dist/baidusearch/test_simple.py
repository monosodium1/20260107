from baidu_search import BaiduSearchCrawler

crawler = BaiduSearchCrawler()
results = crawler.search('人工智能', 1, 5)
print(f'结果数: {len(results)}')
for i, r in enumerate(results[:3]):
    print(f'{i+1}. {r["title"]}')
crawler.close()
