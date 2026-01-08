from app.models import AIModel, AIModelUsage
from app import db
from datetime import datetime
import json


class AIModelService:
    """AI模型管理服务"""

    @staticmethod
    def get_all_models():
        """
        获取所有模型

        Returns:
            list: 模型列表
        """
        return AIModel.query.order_by(AIModel.created_at.desc()).all()

    @staticmethod
    def get_active_models():
        """
        获取活跃的模型

        Returns:
            list: 活跃模型列表
        """
        return AIModel.query.filter_by(status='active').order_by(AIModel.created_at.desc()).all()

    @staticmethod
    def get_default_model():
        """
        获取默认模型

        Returns:
            AIModel: 默认模型对象
        """
        return AIModel.query.filter_by(is_default=True, status='active').first()

    @staticmethod
    def get_model_by_id(model_id):
        """
        根据ID获取模型

        Args:
            model_id: 模型ID

        Returns:
            AIModel: 模型对象
        """
        return AIModel.query.get(model_id)

    @staticmethod
    def create_model(data):
        """
        创建模型

        Args:
            data: 模型数据字典

        Returns:
            AIModel: 创建的模型对象
        """
        is_default = data.get('is_default', False)
        
        if is_default:
            AIModel.query.filter_by(is_default=True).update({'is_default': False})
        
        model = AIModel(
            name=data['name'],
            api_url=data['api_url'],
            api_key=data['api_key'],
            model_name=data['model_name'],
            system_prompt=data.get('system_prompt', ''),
            status=data.get('status', 'active'),
            is_default=is_default
        )
        
        db.session.add(model)
        db.session.commit()
        
        return model

    @staticmethod
    def update_model(model_id, data):
        """
        更新模型

        Args:
            model_id: 模型ID
            data: 模型数据字典

        Returns:
            bool: 是否更新成功
        """
        model = AIModel.query.get(model_id)
        if not model:
            return False
        
        is_default = data.get('is_default', False)
        
        if is_default and not model.is_default:
            AIModel.query.filter_by(is_default=True).update({'is_default': False})
        
        model.name = data.get('name', model.name)
        model.api_url = data.get('api_url', model.api_url)
        model.api_key = data.get('api_key', model.api_key)
        model.model_name = data.get('model_name', model.model_name)
        model.system_prompt = data.get('system_prompt', model.system_prompt)
        model.status = data.get('status', model.status)
        model.is_default = is_default
        
        db.session.commit()
        return True

    @staticmethod
    def delete_model(model_id):
        """
        删除模型

        Args:
            model_id: 模型ID

        Returns:
            bool: 是否删除成功
        """
        model = AIModel.query.get(model_id)
        if model:
            db.session.delete(model)
            db.session.commit()
            return True
        return False

    @staticmethod
    def set_default_model(model_id):
        """
        设置默认模型

        Args:
            model_id: 模型ID

        Returns:
            bool: 是否设置成功
        """
        model = AIModel.query.get(model_id)
        if not model:
            return False
        
        AIModel.query.filter_by(is_default=True).update({'is_default': False})
        model.is_default = True
        db.session.commit()
        
        return True

    @staticmethod
    def record_usage(model_id, prompt_tokens, completion_tokens, request_type='chat'):
        """
        记录模型使用情况

        Args:
            model_id: 模型ID
            prompt_tokens: 提示词token数
            completion_tokens: 完成token数
            request_type: 请求类型

        Returns:
            AIModelUsage: 使用记录对象
        """
        total_tokens = prompt_tokens + completion_tokens
        
        usage = AIModelUsage(
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            request_type=request_type
        )
        
        db.session.add(usage)
        db.session.commit()
        
        return usage

    @staticmethod
    def get_usage_stats(model_id=None, days=30):
        """
        获取使用统计

        Args:
            model_id: 模型ID（可选）
            days: 统计天数

        Returns:
            dict: 统计信息
        """
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = AIModelUsage.query.filter(AIModelUsage.created_at >= start_date)
        
        if model_id:
            query = query.filter_by(model_id=model_id)
        
        records = query.all()
        
        total_tokens = sum(r.total_tokens for r in records)
        total_requests = len(records)
        
        return {
            'total_tokens': total_tokens,
            'total_requests': total_requests,
            'avg_tokens_per_request': total_tokens / total_requests if total_requests > 0 else 0,
            'days': days
        }

    @staticmethod
    def get_usage_history(model_id=None, page=1, per_page=20):
        """
        获取使用历史

        Args:
            model_id: 模型ID（可选）
            page: 页码
            per_page: 每页数量

        Returns:
            dict: 包含数据和分页信息的字典
        """
        query = AIModelUsage.query
        
        if model_id:
            query = query.filter_by(model_id=model_id)
        
        query = query.order_by(AIModelUsage.created_at.desc())
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'data': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
