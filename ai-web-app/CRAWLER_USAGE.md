# 爬虫管理功能使用说明

## 功能概述

爬虫管理模块已成功集成到系统中，提供以下功能：

### 1. 爬虫源管理
- 新增爬虫源（支持百度搜索、Google搜索等）
- 编辑爬虫源配置
- 删除爬虫源
- 查看爬虫源状态

### 2. 任务管理
- 创建爬虫任务
- 启动/停止任务
- 查看任务进度
- 删除任务

### 3. 数据查看
- 查看采集的数据
- 按任务筛选数据
- 查看数据详情

## 使用方法

### 1. 访问爬虫管理页面

登录系统后，点击导航菜单中的"爬虫管理"按钮，或直接访问：
```
http://localhost:5000/crawler-management
```

### 2. 创建爬虫源

1. 点击"新增源"按钮
2. 填写源信息：
   - 源名称：例如"百度搜索源"
   - 源类型：选择"百度搜索"
   - URL：可选，填写目标URL
3. 点击"保存"

### 3. 创建爬虫任务

1. 点击"新增任务"按钮
2. 填写任务信息：
   - 任务名称：例如"搜索林俊杰"
   - 爬虫源：选择之前创建的源
   - 搜索关键词：例如"林俊杰"
   - 起始页：默认1
   - 总页数：例如3页
   - 每页数量：默认10条
3. 点击"创建任务"

### 4. 执行任务

1. 在任务列表中找到创建的任务
2. 点击绿色的"播放"图标启动任务
3. 任务状态会显示为"运行中"，进度条会实时更新
4. 任务完成后，状态变为"已完成"

### 5. 查看采集数据

1. 在页面底部的"采集数据"区域查看所有数据
2. 可以通过下拉框选择特定任务来筛选数据
3. 点击URL链接可以跳转到原始页面

## 技术架构

### 百度搜索爬虫模块

位置：`dist/baidusearch/`

主要文件：
- `baidu_search.py` - 百度搜索爬虫核心类
- `search_cli.py` - 命令行工具
- `__init__.py` - 模块初始化

### 数据模型

- `CrawlerSource` - 爬虫源模型
- `CrawlerTask` - 爬虫任务模型
- `CrawlerData` - 爬虫数据模型

### 服务层

- `CrawlerService` - 爬虫服务类，提供所有爬虫相关业务逻辑

### API接口

- `GET /api/crawler/stats` - 获取统计信息
- `GET /api/crawler/sources` - 获取爬虫源列表
- `POST /api/crawler/sources` - 创建爬虫源
- `PUT /api/crawler/sources/<id>` - 更新爬虫源
- `DELETE /api/crawler/sources/<id>` - 删除爬虫源
- `GET /api/crawler/tasks` - 获取任务列表
- `POST /api/crawler/tasks` - 创建任务
- `POST /api/crawler/tasks/<id>/run` - 启动任务
- `POST /api/crawler/tasks/<id>/stop` - 停止任务
- `DELETE /api/crawler/tasks/<id>` - 删除任务
- `GET /api/crawler/data` - 获取采集数据

## 命令行使用示例

也可以直接使用命令行工具运行爬虫：

```bash
cd dist/baidusearch
python search_cli.py --wd "林俊杰" --page 1 --limit 5
```

参数说明：
- `--wd` 或 `--keyword`: 搜索关键词（必需）
- `--page`: 起始页码（默认1）
- `--limit`: 每页结果数量（默认10）
- `--pages`: 总页数（默认1）
- `--output` 或 `-o`: 输出文件路径（JSON格式）
- `--verbose` 或 `-v`: 显示详细信息

## 注意事项

1. **网络连接**：确保服务器可以访问百度搜索引擎
2. **频率限制**：避免频繁请求，建议设置合理的页数和延迟
3. **数据存储**：所有采集的数据会存储在SQLite数据库中
4. **任务管理**：可以同时运行多个任务，但建议控制并发数量
5. **错误处理**：任务失败时会记录错误信息，可以查看任务详情

## 扩展开发

要添加新的爬虫源类型：

1. 在 `dist/` 目录下创建新的爬虫模块
2. 在 `CrawlerService._execute_task()` 方法中添加新的爬虫类型支持
3. 在前端页面的源类型下拉框中添加新选项

示例：

```python
# 在 crawler_service.py 中添加
if source.source_type == 'google':
    from google_search import GoogleSearchCrawler
    crawler = GoogleSearchCrawler()
```

## 系统状态

当前系统运行在：http://localhost:5000

登录凭据：
- 用户名：admin
- 密码：123456
