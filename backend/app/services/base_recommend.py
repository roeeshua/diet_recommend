from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RecommendServiceBase(ABC):
    """推荐服务的抽象接口，所有实现都必须继承这个类"""
    
    @abstractmethod
    def get_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """获取推荐食材列表
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            食材字典列表，每个字典包含 id, name, category, calories, tags
        """
        pass
    
    @abstractmethod
    def generate_meal_plan(self, user_id: int, date: str) -> Dict[str, Any]:
        """生成每日饮食计划
        
        Args:
            user_id: 用户ID
            date: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            包含 breakfast, lunch, dinner 的字典
        """
        pass