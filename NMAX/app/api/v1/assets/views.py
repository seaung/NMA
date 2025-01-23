from rest_framework import viewsets, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from app.models.assets.assets import Assets
from .serializers import AssetsSerializer


class AssetsManagerViewSets(viewsets.ModelViewSet):
    """资产管理视图集
    
    提供资产的增删改查功能
    需要JWT认证和登录权限
    """
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = AssetsSerializer
    queryset = Assets.objects.all()

    def get_queryset(self):
        """获取资产查询集
        
        根据用户权限和查询参数过滤资产列表
        普通用户只能查看自己部门的资产
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 如果不是超级用户，只能查看自己部门的资产
        if not user.is_superuser:
            queryset = queryset.filter(department=user.department)
            
        # 根据查询参数过滤
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(description__icontains=search)
            )
            
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        asset_type = self.request.query_params.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
            
        return queryset

    def create(self, request: Request) -> Response:
        """创建新资产
        
        Args:
            request: 包含资产信息的请求
            
        Returns:
            201: 创建成功
            400: 创建失败
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """更新资产信息
        
        Args:
            request: 包含更新信息的请求
            
        Returns:
            200: 更新成功
            400: 更新失败
        """
        asset = self.get_object()
        serializer = self.get_serializer(asset, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """删除资产
        
        Returns:
            204: 删除成功
        """
        asset = self.get_object()
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

