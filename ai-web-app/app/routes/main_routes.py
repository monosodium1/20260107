from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import random
import json
from app.models import User
from app.services.crawler_service import crawler_service
from app.services.collection_service import collection_service
from app.services.data_service import DataService
from app.services.ai_model_service import AIModelService
from app.services.ai_client import AIClient
from app.services.deep_collection_service import deep_collection_service
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == '123456':
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return jsonify({'success': True, 'message': '登录成功，正在跳转...'})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误，请重试。'})
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/collection')
@login_required
def collection():
    return render_template('collection.html')

@bp.route('/crawler-management')
@login_required
def crawler_management():
    return render_template('crawler_management.html')

@bp.route('/data')
@login_required
def data():
    return render_template('data.html')

@bp.route('/deep-collection')
@login_required
def deep_collection():
    return render_template('deep_collection.html')

@bp.route('/ai-model')
@login_required
def ai_model():
    return render_template('ai_model.html')

@bp.route('/ai-analysis')
@login_required
def ai_analysis():
    return render_template('ai_analysis.html')

@bp.route('/big-screen')
@login_required
def big_screen():
    return render_template('big_screen.html')

@bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    stats = {
        'total_data': 1234567,
        'total_crawls': 89123,
        'ai_engine_status': '运行中',
        'network_status': '正常',
        'system_status': '警告',
        'data_growth_24h': '+12.5%',
        'crawls_per_hour': '~500/h',
        'ai_model_version': 'V2.1',
        'system_warning': '需关注存储'
    }
    return jsonify(stats)

@bp.route('/api/dashboard/trend')
@login_required
def dashboard_trend():
    trend_data = {
        'days': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        'crawls': [1200, 1550, 1300, 1800, 2100, 900, 1100],
        'data': [15000, 18200, 16500, 22000, 25500, 11000, 14000]
    }
    return jsonify(trend_data)

@bp.route('/api/dashboard/ai-distribution')
@login_required
def ai_distribution():
    ai_data = [
        {'value': 450, 'name': '情感分析'},
        {'value': 320, 'name': '主题分类'},
        {'value': 280, 'name': '实体识别'},
        {'value': 180, 'name': '舆情预警'},
        {'value': 150, 'name': '报告生成'}
    ]
    return jsonify(ai_data)

@bp.route('/api/dashboard/logs')
@login_required
def dashboard_logs():
    logs = [
        {'time': '2024-07-25 10:30:15', 'user': 'Admin', 'module': '采集管理', 'desc': '启动爬虫任务: 财经门户A', 'status': '成功'},
        {'time': '2024-07-25 10:25:01', 'user': 'System', 'module': 'AI分析', 'desc': '执行情感分析批处理', 'status': '成功'},
        {'time': '2024-07-25 09:55:40', 'user': 'User001', 'module': '数据管理', 'desc': '导出数据: 20240724', 'status': '成功'},
        {'time': '2024-07-25 09:10:11', 'user': 'Admin', 'module': '采集管理', 'desc': '停止爬虫任务: 社交媒体B', 'status': '失败'},
        {'time': '2024-07-25 08:00:00', 'user': 'System', 'module': '系统', 'desc': '每日数据备份开始', 'status': '成功'}
    ]
    return jsonify(logs)

@bp.route('/api/crawler/stats', methods=['GET'])
@login_required
def crawler_stats():
    stats = crawler_service.get_stats()
    return jsonify(stats)

@bp.route('/api/crawler/sources', methods=['GET', 'POST'])
@login_required
def crawler_sources():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        headers = data.get('headers')
        if headers and isinstance(headers, str):
            import json
            try:
                headers = json.loads(headers)
            except:
                headers = None
        
        data_selector = data.get('data_selector')
        if data_selector and isinstance(data_selector, str):
            import json
            try:
                data_selector = json.loads(data_selector)
            except:
                data_selector = None
        
        body_template = data.get('body_template')
        if body_template and isinstance(body_template, str):
            import json
            try:
                body_template = json.loads(body_template)
            except:
                body_template = body_template
        
        source = crawler_service.create_source(
            name=data.get('name'),
            source_type=data.get('source_type'),
            url=data.get('url'),
            description=data.get('description'),
            method=data.get('method', 'GET'),
            status=data.get('status', 'active'),
            headers=headers,
            body_template=body_template,
            data_selector=data_selector,
            title_selector=data.get('title_selector'),
            url_selector=data.get('url_selector'),
            summary_selector=data.get('summary_selector'),
            image_selector=data.get('image_selector'),
            config={}
        )
        return jsonify({'success': True, 'source': source.to_dict()})
    else:
        sources = crawler_service.get_sources()
        return jsonify({'sources': [s.to_dict() for s in sources]})

@bp.route('/api/crawler/sources/<int:source_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def crawler_source_detail(source_id):
    if request.method == 'GET':
        source = crawler_service.get_source(source_id)
        if source:
            return jsonify({'source': source.to_dict()})
        return jsonify({'error': 'Source not found'}), 404
    
    elif request.method == 'PUT':
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        headers = data.get('headers')
        if headers and isinstance(headers, str):
            import json
            try:
                headers = json.loads(headers)
            except:
                headers = None
        
        data_selector = data.get('data_selector')
        if data_selector and isinstance(data_selector, str):
            import json
            try:
                data_selector = json.loads(data_selector)
            except:
                data_selector = None
        
        body_template = data.get('body_template')
        if body_template and isinstance(body_template, str):
            import json
            try:
                body_template = json.loads(body_template)
            except:
                body_template = body_template
        
        update_data = {
            'name': data.get('name'),
            'source_type': data.get('source_type'),
            'url': data.get('url'),
            'description': data.get('description'),
            'method': data.get('method', 'GET'),
            'status': data.get('status', 'active'),
            'headers': headers,
            'body_template': body_template,
            'data_selector': data_selector,
            'title_selector': data.get('title_selector'),
            'url_selector': data.get('url_selector'),
            'summary_selector': data.get('summary_selector'),
            'image_selector': data.get('image_selector')
        }
        
        source = crawler_service.update_source(source_id, **update_data)
        if source:
            return jsonify({'success': True, 'source': source.to_dict()})
        return jsonify({'error': 'Source not found'}), 404
    
    elif request.method == 'DELETE':
        success = crawler_service.delete_source(source_id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Source not found'}), 404

@bp.route('/api/crawler/tasks', methods=['GET', 'POST'])
@login_required
def crawler_tasks():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form.to_dict()
        task = crawler_service.create_task(
            source_id=int(data.get('source_id')),
            task_name=data.get('task_name'),
            keyword=data.get('keyword'),
            page=int(data.get('page', 1)),
            limit=int(data.get('limit', 10)),
            pages=int(data.get('pages', 1))
        )
        return jsonify({'success': True, 'task': task.to_dict()})
    else:
        source_id = request.args.get('source_id', type=int)
        status = request.args.get('status')
        tasks = crawler_service.get_tasks(source_id=source_id, status=status)
        return jsonify({'tasks': [t.to_dict() for t in tasks]})

@bp.route('/api/crawler/tasks/<int:task_id>', methods=['GET', 'DELETE'])
@login_required
def crawler_task_detail(task_id):
    if request.method == 'GET':
        task = crawler_service.get_task(task_id)
        if task:
            return jsonify({'task': task.to_dict()})
        return jsonify({'error': 'Task not found'}), 404
    
    elif request.method == 'DELETE':
        success = crawler_service.delete_task(task_id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Task not found'}), 404

@bp.route('/api/crawler/tasks/<int:task_id>/run', methods=['POST'])
@login_required
def crawler_task_run(task_id):
    success = crawler_service.run_task(task_id)
    if success:
        return jsonify({'success': True, 'message': '任务已启动'})
    return jsonify({'success': False, 'message': '任务启动失败或已在运行中'})

@bp.route('/api/crawler/tasks/<int:task_id>/stop', methods=['POST'])
@login_required
def crawler_task_stop(task_id):
    success = crawler_service.stop_task(task_id)
    if success:
        return jsonify({'success': True, 'message': '任务已停止'})
    return jsonify({'success': False, 'message': '任务停止失败'})

@bp.route('/api/crawler/data', methods=['GET'])
@login_required
def crawler_data():
    task_id = request.args.get('task_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    data = crawler_service.get_task_data(task_id, limit=limit, offset=offset)
    return jsonify({'data': [d.to_dict() for d in data]})

@bp.route('/api/collection/sources', methods=['GET'])
@login_required
def collection_sources():
    sources = collection_service.get_available_sources()
    return jsonify({'sources': sources})

@bp.route('/api/collection/start', methods=['POST'])
@login_required
def collection_start():
    keyword = request.form.get('keyword')
    source_ids = json.loads(request.form.get('source_ids', '[]'))
    page = int(request.form.get('page', 1))
    pages = int(request.form.get('pages', 1))
    limit = int(request.form.get('limit', 10))
    
    collection_id = collection_service.start_collection(keyword, source_ids, page, pages, limit)
    return jsonify({'collection_id': collection_id})

@bp.route('/api/collection/stream', methods=['GET'])
@login_required
def collection_stream():
    collection_id = request.args.get('collection_id')
    
    def generate():
        for data in collection_service.get_collection_data(collection_id):
            yield data
    
    return Response(generate(), mimetype='text/event-stream')

@bp.route('/api/collection/save', methods=['POST'])
@login_required
def collection_save():
    data = json.loads(request.form.get('data', '[]'))
    saved_count = collection_service.save_collection_data(data)
    return jsonify({'saved_count': saved_count})

@bp.route('/api/collection/stop', methods=['POST'])
@login_required
def collection_stop():
    collection_id = request.form.get('collection_id')
    success = collection_service.stop_collection(collection_id)
    if success:
        return jsonify({'success': True, 'message': '采集已停止'})
    return jsonify({'success': False, 'message': '停止失败'})

@bp.route('/api/data/list', methods=['GET'])
@login_required
def data_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', None)
    
    result = DataService.get_data_list(page, per_page, search_query)
    return jsonify(result)

@bp.route('/api/data/stats', methods=['GET'])
@login_required
def data_stats():
    stats = DataService.get_data_stats()
    return jsonify(stats)

@bp.route('/api/data/<int:data_id>', methods=['DELETE'])
@login_required
def delete_data(data_id):
    success = DataService.delete_data(data_id)
    if success:
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'})

@bp.route('/api/data/batch-delete', methods=['POST'])
@login_required
def batch_delete_data():
    data = request.get_json()
    data_ids = data.get('data_ids', [])
    
    if not data_ids:
        return jsonify({'success': False, 'message': '请选择要删除的数据'})
    
    count = DataService.batch_delete_data(data_ids)
    return jsonify({'success': True, 'message': f'成功删除 {count} 条数据', 'count': count})

@bp.route('/api/data/batch-deep-collect', methods=['POST'])
@login_required
def batch_deep_collect():
    data = request.get_json()
    data_ids = data.get('data_ids', [])
    
    if not data_ids:
        return jsonify({'success': False, 'message': '请选择要进行深度采集的数据'})
    
    return jsonify({'success': True, 'message': f'已将 {len(data_ids)} 条数据加入深度采集队列', 'count': len(data_ids)})

@bp.route('/api/ai-models', methods=['GET'])
@login_required
def ai_models_list():
    models = AIModelService.get_all_models()
    return jsonify({'models': [model.to_dict() for model in models]})

@bp.route('/api/ai-models', methods=['POST'])
@login_required
def create_ai_model():
    data = request.get_json()
    
    required_fields = ['name', 'api_url', 'api_key', 'model_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'})
    
    try:
        model = AIModelService.create_model(data)
        return jsonify({'success': True, 'message': '模型创建成功', 'model': model.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})

@bp.route('/api/ai-models/<int:model_id>', methods=['PUT'])
@login_required
def update_ai_model(model_id):
    data = request.get_json()
    
    try:
        success = AIModelService.update_model(model_id, data)
        if success:
            return jsonify({'success': True, 'message': '模型更新成功'})
        else:
            return jsonify({'success': False, 'message': '模型不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

@bp.route('/api/ai-models/<int:model_id>', methods=['DELETE'])
@login_required
def delete_ai_model(model_id):
    success = AIModelService.delete_model(model_id)
    if success:
        return jsonify({'success': True, 'message': '模型删除成功'})
    return jsonify({'success': False, 'message': '模型不存在'})

@bp.route('/api/ai-models/<int:model_id>/set-default', methods=['POST'])
@login_required
def set_default_ai_model(model_id):
    success = AIModelService.set_default_model(model_id)
    if success:
        return jsonify({'success': True, 'message': '默认模型设置成功'})
    return jsonify({'success': False, 'message': '模型不存在'})

@bp.route('/api/ai-models/<int:model_id>/test', methods=['POST'])
@login_required
def test_ai_model(model_id):
    model = AIModelService.get_model_by_id(model_id)
    if not model:
        return jsonify({'success': False, 'message': '模型不存在'})
    
    client = AIClient(
        api_url=model.api_url,
        api_key=model.api_key,
        model_name=model.model_name,
        system_prompt=model.system_prompt
    )
    
    result = client.test_connection()
    return jsonify(result)

@bp.route('/api/ai-models/<int:model_id>/stats', methods=['GET'])
@login_required
def ai_model_stats(model_id):
    days = request.args.get('days', 30, type=int)
    stats = AIModelService.get_usage_stats(model_id, days)
    return jsonify(stats)

@bp.route('/api/ai-models/<int:model_id>/usage', methods=['GET'])
@login_required
def ai_model_usage(model_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = AIModelService.get_usage_history(model_id, page, per_page)
    return jsonify(result)

@bp.route('/api/ai-models/stats', methods=['GET'])
@login_required
def ai_models_overall_stats():
    days = request.args.get('days', 30, type=int)
    stats = AIModelService.get_usage_stats(None, days)
    return jsonify(stats)

@bp.route('/api/ai-models/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.get_json()
    
    model_id = data.get('model_id')
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({'success': False, 'message': '消息不能为空'})
    
    model = None
    if model_id:
        model = AIModelService.get_model_by_id(model_id)
    else:
        model = AIModelService.get_default_model()
    
    if not model:
        return jsonify({'success': False, 'message': '未找到可用的AI模型'})
    
    client = AIClient(
        api_url=model.api_url,
        api_key=model.api_key,
        model_name=model.model_name,
        system_prompt=model.system_prompt
    )
    
    result = client.chat(messages)
    
    if result['success']:
        AIModelService.record_usage(
            model_id=model.id,
            prompt_tokens=result['prompt_tokens'],
            completion_tokens=result['completion_tokens'],
            request_type='chat'
        )
    
    return jsonify(result)


@bp.route('/api/deep-collection/start', methods=['POST'])
@login_required
def start_deep_collection():
    data = request.get_json()
    collection_data_ids = data.get('collection_data_ids', [])
    ai_model_id = data.get('ai_model_id')
    
    if not collection_data_ids:
        return jsonify({'success': False, 'message': '请选择要深度采集的数据'})
    
    if not ai_model_id:
        return jsonify({'success': False, 'message': '请选择AI模型'})
    
    result = deep_collection_service.start_deep_collection(
        collection_data_ids, ai_model_id
    )
    
    return jsonify(result)


@bp.route('/api/deep-collection/status/<task_id>', methods=['GET'])
@login_required
def deep_collection_status(task_id):
    status = deep_collection_service.get_task_status(task_id)
    if status:
        return jsonify({'success': True, 'status': status})
    return jsonify({'success': False, 'message': '任务不存在'})


@bp.route('/api/deep-collection/list', methods=['GET'])
@login_required
def deep_collection_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', None)
    
    result = deep_collection_service.get_deep_collections(
        page=page, per_page=per_page, search_query=search_query
    )
    
    return jsonify(result)


@bp.route('/api/deep-collection/<int:collection_data_id>', methods=['GET'])
@login_required
def get_deep_collection_detail(collection_data_id):
    deep_collection = deep_collection_service.get_deep_collection(collection_data_id)
    if deep_collection:
        return jsonify({'success': True, 'data': deep_collection.to_dict()})
    return jsonify({'success': False, 'message': '深度采集数据不存在'})


@bp.route('/api/deep-collection/delete', methods=['POST'])
@login_required
def delete_deep_collections():
    data = request.get_json()
    collection_data_ids = data.get('collection_data_ids', [])
    
    if not collection_data_ids:
        return jsonify({'success': False, 'message': '请选择要删除的数据'})
    
    count = deep_collection_service.delete_deep_collections(collection_data_ids)
    
    return jsonify({
        'success': True,
        'message': f'成功删除 {count} 条深度采集数据'
    })


@bp.route('/api/deep-collection/stats', methods=['GET'])
@login_required
def deep_collection_stats():
    stats = deep_collection_service.get_stats()
    return jsonify(stats)


