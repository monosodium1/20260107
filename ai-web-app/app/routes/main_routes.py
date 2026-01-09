from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import random
import json
from app.models import User, CollectionData, CrawlerTask
from app.services.crawler_service import crawler_service
from app.services.collection_service import collection_service
from app.services.data_service import DataService
from app.services.ai_model_service import AIModelService
from app.services.ai_client import AIClient
from app.services.deep_collection_service import deep_collection_service
from app.services.system_monitor_service import system_monitor_service
from app.services.ai_analysis_service import AIAnalysisService
from app.services.chat_session_service import ChatSessionService
from flask_login import current_user
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
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            session.permanent = True
            return jsonify({'success': True, 'message': '登录成功，正在跳转...'})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误，请重试。'})
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': '用户名至少需要3个字符'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少需要6个字符'})
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'})
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '注册成功，请登录'})
    
    return render_template('register.html')

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
    stats = system_monitor_service.get_dashboard_stats()
    
    data_growth_24h = '+0%'
    try:
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_count = CollectionData.query.filter(CollectionData.saved_at >= yesterday).count()
        if yesterday_count > 0:
            total_data = stats['total_data']
            growth_percent = (yesterday_count / total_data) * 100
            data_growth_24h = f'+{growth_percent:.1f}%'
    except:
        pass
    
    crawls_per_hour = '~0/h'
    if stats['total_crawls'] > 0:
        try:
            from datetime import timedelta
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_crawls = CrawlerTask.query.filter(CrawlerTask.created_at >= one_hour_ago).count()
            crawls_per_hour = f'~{recent_crawls}/h'
        except:
            pass
    
    ai_model_version = '未配置'
    try:
        from app.models import AIModel
        ai_model = AIModel.query.filter_by(is_default=True).first()
        if ai_model:
            ai_model_version = ai_model.model_name
    except:
        pass
    
    return jsonify({
        'total_data': stats['total_data'],
        'total_crawls': stats['total_crawls'],
        'ai_engine_status': stats['ai_engine_status'],
        'network_status': stats['network_status'],
        'system_status': stats['system_status'],
        'data_growth_24h': data_growth_24h,
        'crawls_per_hour': crawls_per_hour,
        'ai_model_version': ai_model_version,
        'system_warning': stats['system_warning']
    })

@bp.route('/api/dashboard/trend')
@login_required
def dashboard_trend():
    trend_data = system_monitor_service.get_data_trend(days=7)
    return jsonify(trend_data)

@bp.route('/api/dashboard/ai-distribution')
@login_required
def ai_distribution():
    ai_data = system_monitor_service.get_ai_distribution()
    return jsonify(ai_data)

@bp.route('/api/dashboard/logs')
@login_required
def dashboard_logs():
    logs = system_monitor_service.get_system_logs(limit=10)
    return jsonify(logs)

@bp.route('/api/dashboard/source-distribution')
@login_required
def source_distribution():
    distribution = system_monitor_service.get_data_source_distribution()
    return jsonify(distribution)

@bp.route('/api/dashboard/system-status')
@login_required
def system_status():
    status = system_monitor_service.get_system_status()
    return jsonify(status)

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
    
    data = crawler_service.get_all_data(limit=limit, offset=offset)
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


@bp.route('/api/ai-model/active', methods=['GET'])
@login_required
def get_active_ai_models():
    models = AIModelService.get_active_models()
    default_model = AIModelService.get_default_model()
    
    return jsonify({
        'success': True,
        'models': [model.to_dict() for model in models],
        'default_model': default_model.to_dict() if default_model else None
    })


@bp.route('/api/ai-analysis/chat', methods=['POST'])
@login_required
def ai_analysis_chat():
    message = request.form.get('message')
    model_id = request.form.get('model_id', type=int)
    session_id = request.form.get('session_id', type=int)
    
    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'})
    
    if not model_id:
        return jsonify({'success': False, 'error': '请选择AI模型'})
    
    result = AIAnalysisService.process_message(message, model_id)
    
    if result['success']:
        if session_id:
            ChatSessionService.add_message(
                session_id=session_id,
                role='user',
                content=message,
                message_type='text',
                tokens_used=0
            )
            
            ChatSessionService.add_message(
                session_id=session_id,
                role='assistant',
                content=result.get('message', '') or '',
                message_type=result['type'],
                extra_data={
                    'chart_config': result.get('chart_config'),
                    'table_data': result.get('table_data'),
                    'text': result.get('content')
                },
                tokens_used=0
            )
    
    return jsonify(result)


@bp.route('/api/chat/sessions', methods=['GET'])
@login_required
def get_chat_sessions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = ChatSessionService.get_user_sessions(
        user_id=current_user.id,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'success': True,
        'sessions': result['data'],
        'total': result['total']
    })


@bp.route('/api/chat/sessions', methods=['POST'])
@login_required
def create_chat_session():
    data = request.get_json()
    ai_model_id = data.get('ai_model_id')
    title = data.get('title')
    
    if not ai_model_id:
        return jsonify({'success': False, 'error': '请选择AI模型'})
    
    session = ChatSessionService.create_session(
        user_id=current_user.id,
        ai_model_id=ai_model_id,
        title=title
    )
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })


@bp.route('/api/chat/sessions/<int:session_id>', methods=['GET'])
@login_required
def get_chat_session(session_id):
    session = ChatSessionService.get_session(session_id)
    
    if not session:
        return jsonify({'success': False, 'error': '会话不存在'})
    
    if session.user_id != current_user.id:
        return jsonify({'success': False, 'error': '无权访问此会话'})
    
    messages = ChatSessionService.get_session_messages(session_id)
    
    return jsonify({
        'success': True,
        'session': session.to_dict(),
        'messages': messages
    })


@bp.route('/api/chat/sessions/<int:session_id>', methods=['PUT'])
@login_required
def update_chat_session(session_id):
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({'success': False, 'error': '标题不能为空'})
    
    session = ChatSessionService.get_session(session_id)
    
    if not session:
        return jsonify({'success': False, 'error': '会话不存在'})
    
    if session.user_id != current_user.id:
        return jsonify({'success': False, 'error': '无权修改此会话'})
    
    success = ChatSessionService.update_session_title(session_id, title)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': '更新失败'})


@bp.route('/api/chat/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_chat_session(session_id):
    session = ChatSessionService.get_session(session_id)
    
    if not session:
        return jsonify({'success': False, 'error': '会话不存在'})
    
    if session.user_id != current_user.id:
        return jsonify({'success': False, 'error': '无权删除此会话'})
    
    success = ChatSessionService.delete_session(session_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': '删除失败'})

@bp.route('/api/big-screen/data')
@login_required
def big_screen_data():
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    total_collect = CollectionData.query.count()
    
    success_tasks = CrawlerTask.query.filter_by(status='completed').count()
    total_tasks = CrawlerTask.query.count()
    success_rate = round((success_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
    
    total_sources = crawler_service.get_sources_count()
    
    keywords = ['AI', '大数据', '云计算', '区块链', '物联网']
    total_keywords = len(keywords)
    
    trend_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        count = CollectionData.query.filter(
            func.date(CollectionData.saved_at) == date.date()
        ).count()
        trend_data.append(count)
    
    source_distribution = []
    sources = crawler_service.get_sources()
    for source in sources:
        count = CollectionData.query.filter(
            CollectionData.source == source.name
        ).count()
        if count > 0:
            source_distribution.append({
                'value': count,
                'name': source.name
            })
    
    if not source_distribution:
        source_distribution = [
            {'value': 1048, 'name': '百度'},
            {'value': 735, 'name': '谷歌'},
            {'value': 580, 'name': '必应'},
            {'value': 484, 'name': '知乎'},
            {'value': 300, 'name': '微博'}
        ]
    
    keyword_data = []
    for keyword in keywords:
        count = CollectionData.query.filter(
            CollectionData.title.like(f'%{keyword}%')
        ).count()
        keyword_data.append({
            'name': keyword,
            'value': count
        })
    
    keyword_data.sort(key=lambda x: x['value'], reverse=True)
    
    if not keyword_data or all(item['value'] == 0 for item in keyword_data):
        keyword_data = [
            {'name': 'AI', 'value': 18203},
            {'name': '大数据', 'value': 23489},
            {'name': '云计算', 'value': 29034},
            {'name': '区块链', 'value': 104970},
            {'name': '物联网', 'value': 131744}
        ]
    
    latest_data = CollectionData.query.order_by(
        CollectionData.saved_at.desc()
    ).limit(10).all()
    
    latest_list = []
    for data in latest_data:
        latest_list.append({
            'title': data.title,
            'time': data.saved_at.strftime('%Y-%m-%d %H:%M:%S') if data.saved_at else '未知'
        })
    
    return jsonify({
        'stats': {
            'total_collect': total_collect,
            'success_rate': success_rate,
            'total_sources': total_sources,
            'total_keywords': total_keywords
        },
        'charts': {
            'trend': trend_data,
            'source': source_distribution,
            'keyword': keyword_data
        },
        'latest': latest_list
    })


