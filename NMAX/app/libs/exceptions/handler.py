"""全局异常处理器：将 DRF 异常转换为统一信封"""
from rest_framework.response import Response
from rest_framework.views import exception_handler

CODE_MAP = {
    400: 1001,
    401: 1002,
    403: 1003,
    404: 1004,
    405: 1001,
    429: 1001,
    500: 5000,
}


def _extract_message(data):
    if isinstance(data, dict):
        for key in ("detail", "msg", "message"):
            if key in data:
                val = data[key]
                return val if isinstance(val, str) else str(val)
        # 取第一个字段错误
        for val in data.values():
            if isinstance(val, list) and val:
                return str(val[0])
            return str(val)
    if isinstance(data, str):
        return data
    return "请求失败"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {"code": 5000, "msg": "服务器内部错误", "data": None},
            status=500,
        )

    status_code = response.status_code
    code = CODE_MAP.get(status_code, 5000)
    msg = _extract_message(response.data)
    return Response(
        {"code": code, "msg": msg, "data": response.data},
        status=status_code,
    )
