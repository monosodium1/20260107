from flask_login import UserMixin
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'


class CrawlerSource(db.Model):
    """爬虫源模型"""
    __tablename__ = 'crawler_source'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='爬虫源名称')
    source_type = db.Column(db.String(50), nullable=False, comment='爬虫源类型（custom, baidu, google等）')
    description = db.Column(db.String(500), comment='描述')
    
    url = db.Column(db.String(1000), comment='目标URL模板，支持变量替换如{keyword}')
    method = db.Column(db.String(10), default='GET', comment='请求方法（GET/POST）')
    
    headers = db.Column(db.Text, comment='请求头（JSON格式）')
    body_template = db.Column(db.Text, comment='请求体模板（POST方法使用）')
    
    data_selector = db.Column(db.Text, comment='数据选择器（JSON格式，定义如何提取数据）')
    title_selector = db.Column(db.String(500), comment='标题选择器')
    url_selector = db.Column(db.String(500), comment='URL选择器')
    summary_selector = db.Column(db.String(500), comment='摘要选择器')
    image_selector = db.Column(db.String(500), comment='图片选择器')
    
    config = db.Column(db.Text, comment='其他配置（JSON格式）')
    status = db.Column(db.String(20), default='active', comment='状态（active/inactive）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    tasks = db.relationship('CrawlerTask', backref='source', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'description': self.description,
            'url': self.url,
            'method': self.method,
            'headers': self.headers,
            'body_template': self.body_template,
            'data_selector': self.data_selector,
            'title_selector': self.title_selector,
            'url_selector': self.url_selector,
            'summary_selector': self.summary_selector,
            'image_selector': self.image_selector,
            'config': self.config,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<CrawlerSource {self.name}>'


class CrawlerTask(db.Model):
    """爬虫任务模型"""
    __tablename__ = 'crawler_task'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('crawler_source.id'), nullable=False)
    task_name = db.Column(db.String(100), nullable=False, comment='任务名称')
    keyword = db.Column(db.String(200), comment='搜索关键词')
    page = db.Column(db.Integer, default=1, comment='页码')
    limit = db.Column(db.Integer, default=10, comment='每页数量')
    pages = db.Column(db.Integer, default=1, comment='总页数')
    status = db.Column(db.String(20), default='pending', comment='任务状态（pending/running/completed/failed）')
    progress = db.Column(db.Integer, default=0, comment='进度（0-100）')
    result_count = db.Column(db.Integer, default=0, comment='结果数量')
    error_message = db.Column(db.Text, comment='错误信息')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    started_at = db.Column(db.DateTime, comment='开始时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'source_name': self.source.name if self.source else None,
            'task_name': self.task_name,
            'keyword': self.keyword,
            'page': self.page,
            'limit': self.limit,
            'pages': self.pages,
            'status': self.status,
            'progress': self.progress,
            'result_count': self.result_count,
            'error_message': self.error_message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<CrawlerTask {self.task_name}>'


class CrawlerData(db.Model):
    """爬虫数据模型"""
    __tablename__ = 'crawler_data'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('crawler_task.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False, comment='标题')
    url = db.Column(db.String(1000), comment='URL')
    summary = db.Column(db.Text, comment='摘要')
    info = db.Column(db.String(500), comment='附加信息')
    source = db.Column(db.String(50), comment='来源网站')
    raw_data = db.Column(db.Text, comment='原始数据（JSON格式）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    task = db.relationship('CrawlerTask', backref='data_items', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'info': self.info,
            'source': self.source,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CrawlerData {self.title}>'


class CollectionData(db.Model):
    """采集数据模型（用户保存的数据）"""
    __tablename__ = 'collection_data'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, comment='标题')
    url = db.Column(db.String(1000), comment='URL')
    summary = db.Column(db.Text, comment='摘要')
    source = db.Column(db.String(50), comment='来源网站')
    image_url = db.Column(db.String(1000), comment='封面图片URL')
    keyword = db.Column(db.String(200), comment='搜索关键词')
    source_type = db.Column(db.String(50), comment='爬虫源类型')
    raw_data = db.Column(db.Text, comment='原始数据（JSON格式）')
    collected_at = db.Column(db.DateTime, default=datetime.utcnow, comment='采集时间')
    saved_at = db.Column(db.DateTime, default=datetime.utcnow, comment='保存时间')
    has_deep_collected = db.Column(db.Boolean, default=False, comment='是否已深度采集')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'source': self.source,
            'image_url': self.image_url,
            'keyword': self.keyword,
            'source_type': self.source_type,
            'collected_at': self.collected_at.strftime('%Y-%m-%d %H:%M:%S') if self.collected_at else None,
            'saved_at': self.saved_at.strftime('%Y-%m-%d %H:%M:%S') if self.saved_at else None,
            'has_deep_collected': self.has_deep_collected
        }
    
    def __repr__(self):
        return f'<CollectionData {self.title}>'


class AIModel(db.Model):
    """AI模型配置模型"""
    __tablename__ = 'ai_model'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='模型名称')
    api_url = db.Column(db.String(500), nullable=False, comment='API地址')
    api_key = db.Column(db.String(500), nullable=False, comment='API密钥')
    model_name = db.Column(db.String(200), nullable=False, comment='模型名称')
    system_prompt = db.Column(db.Text, comment='系统提示词')
    status = db.Column(db.String(20), default='active', comment='状态（active/inactive）')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认模型')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'api_url': self.api_url,
            'api_key': self.api_key,
            'model_name': self.model_name,
            'system_prompt': self.system_prompt,
            'status': self.status,
            'is_default': self.is_default,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<AIModel {self.name}>'


class AIModelUsage(db.Model):
    """AI模型使用记录模型"""
    __tablename__ = 'ai_model_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'), nullable=False)
    prompt_tokens = db.Column(db.Integer, default=0, comment='提示词token数')
    completion_tokens = db.Column(db.Integer, default=0, comment='完成token数')
    total_tokens = db.Column(db.Integer, default=0, comment='总token数')
    request_type = db.Column(db.String(50), comment='请求类型（chat/test/deep_collect等）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    model = db.relationship('AIModel', backref='usage_records', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_id': self.model_id,
            'model_name': self.model.name if self.model else None,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'request_type': self.request_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AIModelUsage {self.model_id} - {self.total_tokens} tokens>'


class DeepCollectionData(db.Model):
    """深度采集数据模型"""
    __tablename__ = 'deep_collection_data'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_data_id = db.Column(db.Integer, db.ForeignKey('collection_data.id'), nullable=False, comment='关联的采集数据ID')
    deep_content = db.Column(db.Text, comment='AI深度采集的内容')
    analysis_result = db.Column(db.Text, comment='AI分析结果')
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'), comment='使用的AI模型ID')
    collection_status = db.Column(db.String(20), default='pending', comment='采集状态（pending/processing/completed/failed）')
    error_message = db.Column(db.Text, comment='错误信息')
    tokens_used = db.Column(db.Integer, default=0, comment='使用的Token数量')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    collection_data = db.relationship('CollectionData', backref='deep_collection', lazy=True)
    ai_model = db.relationship('AIModel', backref='deep_collections', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'collection_data_id': self.collection_data_id,
            'title': self.collection_data.title if self.collection_data else None,
            'url': self.collection_data.url if self.collection_data else None,
            'source': self.collection_data.source if self.collection_data else None,
            'deep_content': self.deep_content,
            'analysis_result': self.analysis_result,
            'ai_model_id': self.ai_model_id,
            'ai_model_name': self.ai_model.name if self.ai_model else None,
            'collection_status': self.collection_status,
            'error_message': self.error_message,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DeepCollectionData {self.collection_data_id} - {self.collection_status}>'

