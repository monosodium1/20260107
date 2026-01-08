# AI智能政企瞭望舆情数据采集与分析系统

## 项目简介

这是一个基于Python Flask框架开发的舆情数据采集与分析系统，集成了爬虫技术、AI分析和数据可视化功能。

## 技术栈

- **后端框架**: Flask 3.0.0
- **数据库**: SQLite3
- **AI模型**: OpenAI GPT
- **前端**: HTML5, CSS3, JavaScript
- **UI框架**: Tailwind CSS, Bootstrap
- **图表库**: ECharts
- **图标库**: Font Awesome
- **实时通信**: WebSocket, SSE

## 项目结构

```
ai-web-app/
├── app/                     # Flask应用核心
│   ├── routes/              # 路由层
│   │   ├── ai_routes.py     # AI相关路由
│   │   ├── main_routes.py   # 主页面路由
│   │   └── __init__.py
│   ├── services/            # 业务逻辑层
│   │   ├── ai_service.py    # AI核心逻辑
│   │   └── __init__.py
│   ├── utils/               # 通用工具
│   │   ├── ai_utils.py      # AI数据处理工具
│   │   ├── ws_sse_utils.py  # WebSocket/SSE工具
│   │   └── __init__.py
│   ├── static/              # 前端静态资源
│   │   ├── css/             # CSS样式文件
│   │   ├── js/              # JavaScript文件
│   │   └── models/          # 本地AI模型文件
│   ├── templates/           # HTML5模板
│   │   ├── login.html       # 登录页
│   │   ├── dashboard.html   # 后台主页
│   │   ├── collection.html  # 采集管理
│   │   ├── crawler_management.html  # 爬虫管理
│   │   ├── data.html       # 数据管理
│   │   ├── deep_collection.html    # 深采管理
│   │   ├── ai_model.html   # AI模型管理
│   │   ├── ai_analysis.html  # AI分析与报告
│   │   └── big_screen.html  # 数智大屏
│   ├── config.py            # Flask配置
│   └── __init__.py          # Flask应用初始化
├── tests/                   # 测试文件
├── requirements.txt         # 项目依赖
├── run.py                   # 应用启动入口
├── .gitignore               # Git忽略文件
└── README.md                # 项目说明
```

## 安装步骤

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件，配置以下变量：

```
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
FLASK_CONFIG=development
```

### 5. 运行应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动。

## 功能模块

### 1. 登录模块
- 用户名密码登录
- 默认账号: admin / 123456

### 2. 后台主页
- 系统运行概览
- 数据统计卡片
- 实时数据图表
- 操作日志

### 3. 采集管理
- 爬虫任务配置
- 数据源管理
- 任务调度

### 4. 爬虫管理
- 爬虫实例监控
- 运行日志查看
- 状态管理

### 5. 数据管理
- 数据检索
- 数据清洗
- 数据导出

### 6. 深采管理
- 深度采集任务
- 进度监控
- 结果分析

### 7. AI模型管理
- 模型配置
- 版本控制
- 性能评估

### 8. AI分析与报告
- 情感分析
- 主题分类
- 实体识别
- 报告生成

### 9. 数智大屏
- 实时数据可视化
- 沉浸式展示
- 全屏模式

## 开发说明

### 添加新路由

在 `app/routes/` 目录下创建新的路由文件，并在 `app/__init__.py` 中注册。

### 添加新服务

在 `app/services/` 目录下创建新的服务文件。

### 添加新工具

在 `app/utils/` 目录下创建新的工具文件。

## 注意事项

1. 请确保在虚拟环境中运行应用
2. 生产环境请修改 `SECRET_KEY` 和数据库配置
3. 使用前请配置好 OpenAI API Key
4. 建议使用 Python 3.8+

## 许可证

MIT License
