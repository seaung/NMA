from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_success


class CustomJSONRenderer(JSONRenderer):
    """自定义JSON渲染器
    
    用于统一API响应格式，所有响应都将包含以下字段：
    - code: HTTP状态码
    - message: 响应消息
    - data: 响应数据
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """重写render方法，统一响应格式
        
        Args:
            data: 原始响应数据
            accepted_media_type: 接受的媒体类型
            renderer_context: 渲染上下文
            
        Returns:
            bytes: 渲染后的JSON字节串
        """
        if renderer_context is None:
            renderer_context = {}
            
        # 获取响应对象和状态码
        response = renderer_context.get('response')
        if response is None:
            return super().render(data, accepted_media_type, renderer_context)
            
        status_code = response.status_code
        
        # 构造统一的响应格式
        resp = {
            'code': status_code,
            'message': '操作成功' if is_success(status_code) else '操作失败',
            'data': data
        }
        
        # 处理错误信息
        if not is_success(status_code) and isinstance(data, dict):
            resp['message'] = data.get('detail', resp['message'])
            resp['data'] = None
            
        return super().render(resp, accepted_media_type, renderer_context)