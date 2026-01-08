from app.models import CollectionData
from app import db
from datetime import datetime
import json


class DataService:
    """数据管理服务"""

    @staticmethod
    def get_data_list(page=1, per_page=10, search_query=None):
        """
        获取数据列表

        Args:
            page: 页码
            per_page: 每页数量
            search_query: 搜索关键词

        Returns:
            dict: 包含数据和分页信息的字典
        """
        query = CollectionData.query

        if search_query:
            search_pattern = f'%{search_query}%'
            query = query.filter(
                db.or_(
                    CollectionData.title.like(search_pattern),
                    CollectionData.summary.like(search_pattern),
                    CollectionData.source.like(search_pattern),
                    CollectionData.keyword.like(search_pattern)
                )
            )

        query = query.order_by(CollectionData.saved_at.desc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'data': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }

    @staticmethod
    def get_data_by_id(data_id):
        """
        根据ID获取数据

        Args:
            data_id: 数据ID

        Returns:
            CollectionData: 数据对象
        """
        return CollectionData.query.get(data_id)

    @staticmethod
    def delete_data(data_id):
        """
        删除数据

        Args:
            data_id: 数据ID

        Returns:
            bool: 是否删除成功
        """
        data = CollectionData.query.get(data_id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return True
        return False

    @staticmethod
    def batch_delete_data(data_ids):
        """
        批量删除数据

        Args:
            data_ids: 数据ID列表

        Returns:
            int: 删除的数量
        """
        count = CollectionData.query.filter(
            CollectionData.id.in_(data_ids)
        ).delete(synchronize_session=False)
        db.session.commit()
        return count

    @staticmethod
    def get_data_stats():
        """
        获取数据统计信息

        Returns:
            dict: 统计信息
        """
        total_count = CollectionData.query.count()
        
        source_stats = db.session.query(
            CollectionData.source_type,
            db.func.count(CollectionData.id)
        ).group_by(CollectionData.source_type).all()
        
        return {
            'total_count': total_count,
            'source_stats': [{'source': s[0], 'count': s[1]} for s in source_stats]
        }
