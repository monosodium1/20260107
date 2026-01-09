from app.models import ChatSession, ChatMessage, AIModel, User
from app import db
from datetime import datetime
import json


class ChatSessionService:
    """对话会话服务"""

    @staticmethod
    def create_session(user_id, ai_model_id, title=None):
        """
        创建新会话

        Args:
            user_id: 用户ID
            ai_model_id: AI模型ID
            title: 会话标题（可选）

        Returns:
            ChatSession: 创建的会话对象
        """
        if not title:
            title = f'新对话 {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        session = ChatSession(
            title=title,
            user_id=user_id,
            ai_model_id=ai_model_id
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session

    @staticmethod
    def get_session(session_id):
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            ChatSession: 会话对象
        """
        return ChatSession.query.get(session_id)

    @staticmethod
    def get_user_sessions(user_id, page=1, per_page=20):
        """
        获取用户的所有会话

        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量

        Returns:
            dict: 包含数据和分页信息的字典
        """
        query = ChatSession.query.filter_by(user_id=user_id)
        query = query.order_by(ChatSession.updated_at.desc())
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'data': [session.to_dict() for session in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }

    @staticmethod
    def update_session_title(session_id, title):
        """
        更新会话标题

        Args:
            session_id: 会话ID
            title: 新标题

        Returns:
            bool: 是否更新成功
        """
        session = ChatSession.query.get(session_id)
        if not session:
            return False
        
        session.title = title
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True

    @staticmethod
    def delete_session(session_id):
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否删除成功
        """
        session = ChatSession.query.get(session_id)
        if not session:
            return False
        
        db.session.delete(session)
        db.session.commit()
        
        return True

    @staticmethod
    def add_message(session_id, role, content, message_type='text', extra_data=None, tokens_used=0):
        """
        添加消息

        Args:
            session_id: 会话ID
            role: 角色（user/assistant）
            content: 消息内容
            message_type: 消息类型（text/chart/table/mixed）
            extra_data: 额外数据（JSON格式）
            tokens_used: 使用的Token数量

        Returns:
            ChatMessage: 创建的消息对象
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_type=message_type,
            extra_data=json.dumps(extra_data) if extra_data else None,
            tokens_used=tokens_used
        )
        
        session = ChatSession.query.get(session_id)
        if session:
            session.updated_at = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        
        return message

    @staticmethod
    def get_session_messages(session_id):
        """
        获取会话的所有消息

        Args:
            session_id: 会话ID

        Returns:
            list: 消息列表
        """
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
        return [message.to_dict() for message in messages]

    @staticmethod
    def delete_message(message_id):
        """
        删除消息

        Args:
            message_id: 消息ID

        Returns:
            bool: 是否删除成功
        """
        message = ChatMessage.query.get(message_id)
        if not message:
            return False
        
        db.session.delete(message)
        db.session.commit()
        
        return True

    @staticmethod
    def get_session_stats(session_id):
        """
        获取会话统计信息

        Args:
            session_id: 会话ID

        Returns:
            dict: 统计信息
        """
        messages = ChatMessage.query.filter_by(session_id=session_id).all()
        
        user_messages = [m for m in messages if m.role == 'user']
        assistant_messages = [m for m in messages if m.role == 'assistant']
        
        total_tokens = sum(m.tokens_used for m in messages)
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'total_tokens': total_tokens
        }