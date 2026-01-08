import argparse
import json
import sys
from baidu_search import BaiduSearchCrawler


def main():
    parser = argparse.ArgumentParser(description='百度搜索爬虫命令行工具')
    parser.add_argument('--wd', '--keyword', type=str, required=True, help='搜索关键词')
    parser.add_argument('--page', type=int, default=1, help='页码（从1开始）')
    parser.add_argument('--limit', type=int, default=10, help='每页结果数量')
    parser.add_argument('--pages', type=int, default=1, help='总页数')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径（JSON格式）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')

    args = parser.parse_args()

    crawler = BaiduSearchCrawler()

    try:
        if args.pages > 1:
            results = crawler.search_multiple_pages(args.wd, args.pages, args.limit)
        else:
            results = crawler.search(args.wd, args.page, args.limit)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {args.output}")
        else:
            print(f"\n搜索结果共 {len(results)} 条:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                if args.verbose:
                    print(f"   摘要: {result['summary']}")
                    print(f"   信息: {result['info']}")
                print()

    except KeyboardInterrupt:
        print("\n\n用户中断搜索")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        crawler.close()


if __name__ == '__main__':
    main()
