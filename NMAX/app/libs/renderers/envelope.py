"""统一响应信封渲染器：{code, msg, data}"""
from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        # 已经是信封结构（异常处理器生成）则透传
        if isinstance(data, dict) and "code" in data and "msg" in data and "data" in data:
            return super().render(data, accepted_media_type, renderer_context)

        code = 0
        msg = "success"
        if response is not None and response.status_code >= 400:
            code = 5000
            msg = "error"
        envelope = {"code": code, "msg": msg, "data": data}
        return super().render(envelope, accepted_media_type, renderer_context)
