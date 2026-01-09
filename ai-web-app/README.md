# AI智能政企瞭望舆情数据采集与分析系统

## 项目简介

这是一个基于Python Flask框架开发的舆情数据采集与分析系统，集成了Selenium爬虫技术、AI深度分析和数据可视化功能。系统支持多源数据采集、AI智能分析、对话交互和实时数据监控。

## 技术栈

- **后端框架**: Flask 3.0.0
- **数据库**: SQLite3
- **爬虫技术**: Selenium WebDriver, BeautifulSoup4
- **AI模型**: OpenAI API兼容接口（支持DeepSeek、OpenAI等）
- **前端**: HTML5, CSS3, JavaScript, jQuery
- **UI框架**: Tailwind CSS
- **图标库**: Font Awesome 6.4.0
- **实时通信**: Server-Sent Events (SSE)

## 核心功能

### 1. 用户认证
- 用户名密码登录
- 会话管理
- 默认账号: admin / 123456

### 2. 采集管理
- 多源数据采集（百度搜索等）
- 实时采集进度显示
- 数据保存到数据库
- 支持自定义采集参数（页数、每页数量）

### 3. 爬虫管理
- 爬虫源配置管理
- Selenium自动化爬虫
- 反爬虫策略（随机延迟、User-Agent轮换）
- 支持多种数据提取选择器

### 4. 数据管理
- 数据列表展示
- 封面图片显示
- 数据搜索和筛选
- 批量删除功能
- 数据导出功能

### 5. AI深度采集
- 使用AI对采集数据进行深度分析
- 批量深度采集
- 实时进度监控
- 支持多种AI模型

### 6. AI模型管理
- 添加、编辑、删除AI模型
- 模型测试功能
- 模型对话测试
- 支持自定义API地址和密钥
- 设置默认模型

### 7. AI对话
- 多会话管理
- 实时对话交互
- 会话历史记录
- 支持多种AI模型切换

### 8. 系统监控
- 实时系统状态监控
- CPU、内存使用率
- 磁盘空间监控
- 进程管理

## 项目结构

```
ai-web-app/
├── app/                          # Flask应用核心
│   ├── routes/                   # 路由层
│   │   ├── ai_routes.py          # AI相关路由（模型管理、对话）
│   │   ├── main_routes.py        # 主页面路由（采集、数据管理）
│   │   └── __init__.py
│   ├── services/                 # 业务逻辑层
│   │   ├── ai_client.py         # AI客户端（封装API调用）
│   │   ├── ai_model_service.py  # AI模型管理服务
│   │   ├── ai_service.py       # AI核心服务
│   │   ├── baidu_selenium_crawler.py  # 百度Selenium爬虫
│   │   ├── chat_session_service.py  # 对话会话管理
│   │   ├── collection_service.py  # 数据采集服务
│   │   ├── crawler_service.py   # 爬虫管理服务
│   │   ├── data_service.py     # 数据管理服务
│   │   ├── deep_collection_service.py  # 深度采集服务
│   │   ├── system_monitor_service.py  # 系统监控服务
│   │   ├── universal_crawler.py  # 通用爬虫工厂
│   │   └── __init__.py
│   ├── static/                  # 前端静态资源
│   │   ├── bootstrap/          # Bootstrap CSS/JS
│   │   └── fontawesome-free-6.4.0-web/  # Font Awesome图标
│   ├── templates/               # HTML5模板
│   │   ├── index.html         # 首页
│   │   ├── login.html         # 登录页
│   │   ├── dashboard.html     # 后台主页
│   │   ├── collection.html    # 采集管理
│   │   ├── crawler_management.html  # 爬虫管理
│   │   ├── data.html         # 数据管理
│   │   ├── ai_models.html    # AI模型管理
│   │   ├── ai_chat.html      # AI对话
│   │   └── system_monitor.html  # 系统监控
│   ├── models.py              # 数据库模型
│   ├── config.py              # Flask配置
│   ├── create_test_ai_model.py  # 创建测试AI模型
│   ├── reset_database.py      # 重置数据库
│   └── __init__.py            # Flask应用初始化
├── requirements.txt            # 项目依赖
├── run.py                    # 应用启动入口
├── .gitignore               # Git忽略文件
├── COLLECTION_USAGE.md       # 采集功能使用说明
├── CRAWLER_USAGE.md         # 爬虫功能使用说明
└── README.md               # 项目说明（本文件）
```

## 安装步骤

### 1. 环境要求

- Python 3.8+
- Chrome浏览器（用于Selenium爬虫）
- ChromeDriver（自动管理）

### 2. 创建虚拟环境

```bash
python -m venv venv
```

### 3. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- Flask 3.0.0
- Flask-SQLAlchemy
- Flask-Login
- Selenium
- webdriver-manager
- BeautifulSoup4
- requests

### 5. 初始化数据库

```bash
python run.py
```

首次运行会自动创建数据库和表结构。

### 6. 配置AI模型

访问 `http://localhost:5000/ai-models`，添加AI模型配置：

- **模型名称**: 如 "DeepSeek-OCR"
- **API地址**: 如 "https://api.siliconflow.cn/v1/chat/completions"
- **API密钥**: 你的API密钥
- **模型名称**: 如 "deepseek-ai/DeepSeek-V3"
- **系统提示词**: 可选

### 7. 运行应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动。

## 使用指南

### 数据采集

1. 访问"采集管理"页面
2. 选择爬虫源（如"百度搜索"）
3. 输入搜索关键词
4. 设置采集参数（页数、每页数量）
5. 点击"开始采集"
6. 实时查看采集进度
7. 采集完成后保存数据

### AI深度采集

1. 访问"数据管理"页面
2. 勾选需要深度采集的数据
3. 点击"批量AI深度采集"
4. 选择AI模型
5. 点击"开始采集"
6. 等待AI分析完成

### AI对话

1. 访问"AI对话"页面
2. 点击"新建对话"
3. 选择AI模型
4. 输入问题并发送
5. 查看AI回复

### 系统监控

1. 访问"系统监控"页面
2. 查看实时系统状态
3. 监控CPU、内存、磁盘使用情况

## 数据库模型

### 核心表

- **user**: 用户表
- **crawler_source**: 爬虫源配置表
- **crawler_task**: 爬虫任务表
- **crawler_data**: 爬虫数据表
- **collection_data**: 采集数据表
- **ai_model**: AI模型配置表
- **ai_model_usage**: AI模型使用记录表
- **chat_session**: 对话会话表
- **chat_message**: 对话消息表
- **deep_collection_data**: 深度采集数据表

## 开发说明

### 添加新的爬虫源

1. 在数据库中添加`crawler_source`记录
2. 配置URL模板、选择器等
3. 在`universal_crawler.py`中实现对应的爬虫类
4. 在工厂函数中注册新爬虫

### 添加新的AI模型

1. 访问"AI模型管理"页面
2. 点击"添加模型"
3. 填写模型配置信息
4. 测试模型连接
5. 保存并设置为默认模型（可选）

### 自定义AI提示词

在AI模型配置中可以设置自定义系统提示词，用于控制AI的行为和输出格式。

## 注意事项

1. **Chrome浏览器**: 确保已安装Chrome浏览器，Selenium爬虫需要
2. **API密钥**: 使用AI功能前请配置有效的API密钥
3. **网络连接**: 爬虫和AI调用需要稳定的网络连接
4. **反爬虫**: 百度等网站可能有反爬虫机制，建议控制采集频率
5. **数据备份**: 定期备份数据库文件`app/app.db`
6. **生产环境**: 生产环境请修改`SECRET_KEY`并使用更安全的数据库

## 常见问题

### Q: 采集失败怎么办？
A: 检查网络连接、Chrome浏览器是否正常、是否有验证码页面。

### Q: AI调用超时怎么办？
A: 检查API地址是否正确、网络是否稳定、API密钥是否有效。

### Q: 如何重置数据库？
A: 运行`python app/reset_database.py`，注意会清空所有数据。

### Q: 封面图片不显示？
A: 某些搜索结果可能没有图片，这是正常现象。

## 更新日志

### v1.0.0 (2026-01-09)
- 初始版本发布
- 实现基础采集功能
- 集成AI深度分析
- 添加AI对话功能
- 实现系统监控

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址: [GitHub仓库链接]
- 邮箱: [联系邮箱]
