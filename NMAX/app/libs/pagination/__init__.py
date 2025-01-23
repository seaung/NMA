from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings


class CustomPageNumberPagination(PageNumberPagination):
    """
    自定义页码分页类
    
    继承自DRF的PageNumberPagination，提供以下功能：
    - 可配置的页码参数名
    - 可配置的页面大小参数名
    - 可配置的最大页面大小
    - 统一的响应格式
    """
    # 默认每页数量
    page_size = api_settings.PAGE_SIZE or 10
    # 页码参数
    page_query_param = 'page'
    # 每页数量参数
    page_size_query_param = 'page_size'
    # 最大每页数量
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        重写响应方法，返回统一格式的分页数据
        
        Args:
            data: 分页后的数据列表
            
        Returns:
            Response: 包含分页信息的响应对象
        """
        return Response({
            'data': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'results': data
            }
        })


class CustomCursorPagination(CursorPagination):
    """
    自定义游标分页类
    
    继承自DRF的CursorPagination，提供以下功能：
    - 基于游标的分页，适用于大数据集
    - 可配置的游标参数名
    - 可配置的页面大小参数名
    - 可配置的排序字段
    - 统一的响应格式
    """
    # 默认每页数量
    page_size = api_settings.PAGE_SIZE or 10
    # 游标参数
    cursor_query_param = 'cursor'
    # 排序字段
    ordering = '-created_at'
    # 每页数量参数
    page_size_query_param = 'page_size'
    # 最大每页数量
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        重写响应方法，返回统一格式的分页数据
        
        Args:
            data: 分页后的数据列表
            
        Returns:
            Response: 包含分页信息的响应对象
        """
        return Response({
            'data': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page_size': self.get_page_size(self.request),
                'results': data
            }
        })