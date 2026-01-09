import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("爬虫源详细信息")
print("=" * 60)

cursor.execute("SELECT * FROM crawler_source")
sources = cursor.fetchall()

if sources:
    print(f"\n共有 {len(sources)} 个爬虫源:\n")
    for source in sources:
        print(f"ID: {source[0]}")
        print(f"名称: {source[1]}")
        print(f"类型: {source[2]}")
        print(f"描述: {source[3]}")
        print(f"URL: {source[4]}")
        print(f"方法: {source[5]}")
        print(f"请求头: {source[6]}")
        print(f"请求体模板: {source[7]}")
        print(f"数据选择器: {source[8]}")
        print(f"标题选择器: {source[9]}")
        print(f"URL选择器: {source[10]}")
        print(f"摘要选择器: {source[11]}")
        print(f"图片选择器: {source[12]}")
        print(f"配置: {source[13]}")
        print(f"状态: {source[14]}")
        print(f"创建时间: {source[15]}")
        print(f"更新时间: {source[16]}")
        print("-" * 60)
else:
    print("\n没有爬虫源数据")

print("\n" + "=" * 60)
print("采集数据详细信息")
print("=" * 60)

cursor.execute("SELECT * FROM collection_data")
collections = cursor.fetchall()

if collections:
    print(f"\n共有 {len(collections)} 条采集数据:\n")
    for item in collections:
        print(f"ID: {item[0]}")
        print(f"标题: {item[1]}")
        print(f"URL: {item[2]}")
        print(f"摘要: {item[3]}")
        print(f"来源: {item[4]}")
        print(f"图片URL: {item[5]}")
        print(f"关键词: {item[6]}")
        print(f"源类型: {item[7]}")
        print(f"原始数据: {item[8]}")
        print(f"采集时间: {item[9]}")
        print(f"保存时间: {item[10]}")
        print(f"是否深度采集: {item[11]}")
        print("-" * 60)
else:
    print("\n没有采集数据")

conn.close()