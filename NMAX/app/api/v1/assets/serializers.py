from rest_framework import serializers

from app.models.assets.assets import Asset


class AssetsSerializer(serializers.ModelSerializer):
    """资产序列化器"""

    class Meta:
        model = Asset
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "is_deleted", "deleted_at")

    def validate_ip(self, value):
        if value and Asset.objects.filter(ip=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("该 IP 已存在")
        return value
