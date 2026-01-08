import requests
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional, Callable
from app.models import CollectionData, DeepCollectionData, AIModel
from app.services.ai_client import AIClient
from app import db
import logging

logger = logging.getLogger(__name__)


class DeepCollectionService:
    """深度采集服务类"""

    def __init__(self):
        self.active_tasks = {}

    def start_deep_collection(self, collection_data_ids: List[int], ai_model_id: int, 
                          progress_callback: Optional[Callable] = None) -> Dict:
        """
        启动深度采集任务

        Args:
            collection_data_ids: 采集数据ID列表
            ai_model_id: AI模型ID
            progress_callback: 进度回调函数

        Returns:
            任务信息字典
        """
        task_id = f"deep_collection_{datetime.utcnow().timestamp()}"
        
        thread = threading.Thread(
            target=self._execute_deep_collection,
            args=(collection_data_ids, ai_model_id, task_id, progress_callback)
        )
        thread.daemon = True
        thread.start()

        self.active_tasks[task_id] = {
            'thread': thread,
            'status': 'running',
            'total': len(collection_data_ids),
            'completed': 0,
            'failed': 0
        }

        return {
            'task_id': task_id,
            'status': 'started',
            'total': len(collection_data_ids)
        }

    def _execute_deep_collection(self, collection_data_ids: List[int], ai_model_id: int, 
                            task_id: str, progress_callback: Optional[Callable]):
        """
        执行深度采集的具体逻辑

        Args:
            collection_data_ids: 采集数据ID列表
            ai_model_id: AI模型ID
            task_id: 任务ID
            progress_callback: 进度回调函数
        """
        try:
            ai_model = AIModel.query.get(ai_model_id)
            if not ai_model:
                logger.error(f"AI模型不存在: {ai_model_id}")
                return

            ai_client = AIClient(
                api_url=ai_model.api_url,
                api_key=ai_model.api_key,
                model_name=ai_model.model_name,
                system_prompt=ai_model.system_prompt
            )

            total = len(collection_data_ids)
            completed = 0
            failed = 0

            for idx, data_id in enumerate(collection_data_ids):
                try:
                    collection_data = CollectionData.query.get(data_id)
                    if not collection_data:
                        logger.warning(f"采集数据不存在: {data_id}")
                        failed += 1
                        continue

                    deep_content, analysis_result, tokens_used = self._collect_with_ai(
                        ai_client, collection_data
                    )

                    existing_deep = DeepCollectionData.query.filter_by(
                        collection_data_id=data_id
                    ).first()

                    if existing_deep:
                        existing_deep.deep_content = deep_content
                        existing_deep.analysis_result = analysis_result
                        existing_deep.ai_model_id = ai_model_id
                        existing_deep.tokens_used = tokens_used
                        existing_deep.collection_status = 'completed'
                        existing_deep.error_message = None
                        existing_deep.updated_at = datetime.utcnow()
                    else:
                        deep_collection = DeepCollectionData(
                            collection_data_id=data_id,
                            deep_content=deep_content,
                            analysis_result=analysis_result,
                            ai_model_id=ai_model_id,
                            collection_status='completed',
                            tokens_used=tokens_used
                        )
                        db.session.add(deep_collection)

                    collection_data.has_deep_collected = True
                    db.session.commit()

                    completed += 1

                    if progress_callback:
                        progress = {
                            'current': idx + 1,
                            'total': total,
                            'completed': completed,
                            'failed': failed,
                            'percentage': int(((idx + 1) / total) * 100)
                        }
                        progress_callback(progress)

                except Exception as e:
                    logger.error(f"深度采集失败 (ID: {data_id}): {str(e)}")
                    failed += 1

                    existing_deep = DeepCollectionData.query.filter_by(
                        collection_data_id=data_id
                    ).first()

                    if existing_deep:
                        existing_deep.collection_status = 'failed'
                        existing_deep.error_message = str(e)
                        existing_deep.updated_at = datetime.utcnow()
                    else:
                        deep_collection = DeepCollectionData(
                            collection_data_id=data_id,
                            collection_status='failed',
                            error_message=str(e),
                            ai_model_id=ai_model_id
                        )
                        db.session.add(deep_collection)

                    db.session.commit()

            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'completed'
                self.active_tasks[task_id]['completed'] = completed
                self.active_tasks[task_id]['failed'] = failed

        except Exception as e:
            logger.error(f"深度采集任务执行失败: {str(e)}")
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'failed'
                self.active_tasks[task_id]['error'] = str(e)

    def _collect_with_ai(self, ai_client: AIClient, collection_data: CollectionData) -> tuple:
        """
        使用AI进行深度采集

        Args:
            ai_client: AI客户端
            collection_data: 采集数据

        Returns:
            (deep_content, analysis_result, tokens_used)
        """
        try:
            prompt = self._build_prompt(collection_data)

            response = ai_client.chat([{"role": "user", "content": prompt}])

            if response and 'content' in response:
                deep_content = response['content']
                analysis_result = self._extract_analysis(deep_content)
                tokens_used = response.get('tokens_used', 0)
                return deep_content, analysis_result, tokens_used
            else:
                return "", "AI响应失败", 0

        except Exception as e:
            logger.error(f"AI采集失败: {str(e)}")
            return "", f"采集失败: {str(e)}", 0

    def _build_prompt(self, collection_data: CollectionData) -> str:
        """
        构建AI提示词

        Args:
            collection_data: 采集数据

        Returns:
            提示词字符串
        """
        prompt = f"""请对以下网页信息进行深度采集和分析：

标题：{collection_data.title}

摘要：{collection_data.summary}

来源：{collection_data.source}

关键词：{collection_data.keyword}

请执行以下任务：
1. 访问该网页URL并提取详细内容
2. 对内容进行深度分析和总结
3. 提取关键信息和要点
4. 生成结构化的分析报告

请以JSON格式返回结果，包含以下字段：
- full_content: 网页完整内容
- key_points: 关键要点列表
- summary: 深度分析总结
- tags: 相关标签列表
- sentiment: 情感分析（正面/负面/中性）
- importance: 重要性评分（1-10）

URL：{collection_data.url}
"""

        return prompt

    def _extract_analysis(self, deep_content: str) -> str:
        """
        从深度采集内容中提取分析结果

        Args:
            deep_content: 深度采集内容

        Returns:
            分析结果字符串
        """
        try:
            if '```json' in deep_content:
                json_start = deep_content.find('```json') + 7
                json_end = deep_content.find('```', json_start)
                json_str = deep_content[json_start:json_end].strip()
                return json_str
            elif '{' in deep_content and '}' in deep_content:
                json_start = deep_content.find('{')
                json_end = deep_content.rfind('}') + 1
                json_str = deep_content[json_start:json_end].strip()
                return json_str
            else:
                return deep_content
        except Exception as e:
            logger.error(f"提取分析结果失败: {str(e)}")
            return deep_content

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态字典
        """
        return self.active_tasks.get(task_id)

    def get_deep_collections(self, page: int = 1, per_page: int = 10, 
                         search_query: Optional[str] = None) -> Dict:
        """
        获取深度采集数据列表

        Args:
            page: 页码
            per_page: 每页数量
            search_query: 搜索关键词

        Returns:
            包含数据和分页信息的字典
        """
        query = DeepCollectionData.query.join(CollectionData)

        if search_query:
            search_pattern = f'%{search_query}%'
            query = query.filter(
                db.or_(
                    CollectionData.title.like(search_pattern),
                    DeepCollectionData.deep_content.like(search_pattern),
                    DeepCollectionData.analysis_result.like(search_pattern)
                )
            )

        query = query.order_by(DeepCollectionData.created_at.desc())

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

    def get_deep_collection(self, collection_data_id: int) -> Optional[DeepCollectionData]:
        """
        获取单个深度采集数据

        Args:
            collection_data_id: 采集数据ID

        Returns:
            深度采集数据对象
        """
        return DeepCollectionData.query.filter_by(
            collection_data_id=collection_data_id
        ).first()

    def delete_deep_collections(self, collection_data_ids: List[int]) -> int:
        """
        批量删除深度采集数据

        Args:
            collection_data_ids: 采集数据ID列表

        Returns:
            删除的数量
        """
        count = DeepCollectionData.query.filter(
            DeepCollectionData.collection_data_id.in_(collection_data_ids)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        CollectionData.query.filter(
            CollectionData.id.in_(collection_data_ids)
        ).update({'has_deep_collected': False})
        
        db.session.commit()
        
        return count

    def get_stats(self) -> Dict:
        """
        获取深度采集统计信息

        Returns:
            统计数据字典
        """
        total = DeepCollectionData.query.count()
        completed = DeepCollectionData.query.filter_by(
            collection_status='completed'
        ).count()
        failed = DeepCollectionData.query.filter_by(
            collection_status='failed'
        ).count()
        total_tokens = db.session.query(
            db.func.sum(DeepCollectionData.tokens_used)
        ).scalar() or 0

        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'total_tokens': total_tokens
        }


deep_collection_service = DeepCollectionService()
