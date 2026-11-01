from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from app.libs.permission.data_scope import filter_by_data_scope
from app.libs.permission.permission import HasPermission
from app.models.assets.assets import Asset
from app.services.excel_utils import build_excel_response, read_excel_rows

from .serializers import AssetsSerializer

EXPORT_HEADERS = [
    "ID", "名称", "IP", "主机名", "域名", "类型", "状态", "安全等级",
    "重要程度", "是否暴露", "业务系统", "描述", "创建时间",
]


class AssetsManagerViewSets(viewsets.ModelViewSet):
    """资产管理视图集：增删改查 + 数据范围过滤 + 软删除 + 导入导出"""

    permission_classes = (HasPermission,)
    required_permissions = ["asset:view"]
    serializer_class = AssetsSerializer
    queryset = Asset.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_deleted=False)
        queryset = filter_by_data_scope(queryset, self.request.user, dept_field="department")

        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(ip__icontains=search)
                | Q(hostname__icontains=search)
                | Q(description__icontains=search)
            )

        asset_status = self.request.query_params.get("status")
        if asset_status:
            queryset = queryset.filter(asset_status=asset_status)

        asset_type = self.request.query_params.get("type")
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)

        exposed = self.request.query_params.get("exposed")
        if exposed in ("true", "1", "yes"):
            queryset = queryset.filter(exposed=True)
        elif exposed in ("false", "0", "no"):
            queryset = queryset.filter(exposed=False)

        asset_group = self.request.query_params.get("asset_group")
        if asset_group:
            queryset = queryset.filter(asset_group=asset_group)

        importance = self.request.query_params.get("importance")
        if importance:
            queryset = queryset.filter(importance=importance)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """软删除资产（保留历史与审计）"""
        asset = self.get_object()
        asset.is_deleted = True
        asset.deleted_at = timezone.now()
        asset.save(update_fields=["is_deleted", "deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def export_excel(self, request: Request):
        rows = []
        for a in self.get_queryset().order_by("-created_at"):
            rows.append([
                a.id, a.name, a.ip, a.hostname, a.domain, a.asset_type,
                a.asset_status, a.security_level or "", a.importance,
                "是" if a.exposed else "否", a.business_system, a.description,
                a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "",
            ])
        return build_excel_response(EXPORT_HEADERS, rows, "assets.xlsx")

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def import_excel(self, request: Request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            raise ValidationError({"file": "缺少上传文件"})
        rows = read_excel_rows(file_obj)
        created, skipped, errors = 0, 0, []
        for idx, row in enumerate(rows, start=2):
            name = (row.get("名称") or row.get("name") or "").strip()
            ip = (row.get("IP") or row.get("ip") or "").strip()
            if not name and not ip:
                skipped += 1
                continue
            defaults = {
                "name": name or ip,
                "hostname": (row.get("主机名") or row.get("hostname") or "").strip(),
                "domain": (row.get("域名") or row.get("domain") or "").strip(),
                "asset_type": (row.get("类型") or row.get("asset_type") or "host"),
                "asset_status": (row.get("状态") or row.get("asset_status") or "idle"),
                "security_level": (row.get("安全等级") or row.get("security_level") or None),
                "importance": _to_int(row.get("重要程度") or row.get("importance"), 1),
                "exposed": str(row.get("是否暴露") or row.get("exposed") or "").strip()
                in ("是", "true", "1", "yes"),
                "business_system": (row.get("业务系统") or row.get("business_system") or "").strip(),
                "description": (row.get("描述") or row.get("description") or "").strip(),
                "created_by": request.user,
            }
            try:
                if ip and Asset.objects.filter(ip=ip, is_deleted=False).exists():
                    skipped += 1
                    continue
                Asset.objects.create(ip=ip, **defaults)
                created += 1
            except Exception as e:  # noqa: BLE001
                errors.append(f"第{idx}行: {e}")
        return Response({"created": created, "skipped": skipped, "errors": errors})


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
