from rest_framework import serializers
from app.models.assets.assets import Assets


class AssetsSerializer(serializers.ModelSerializer):
    """资产序列化器
    
    用于资产数据的序列化和反序列化
    """
    class Meta:
        model = Assets
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_serial_number(self, value):
        """验证序列号唯一性
        
        Args:
            value: 序列号值
            
        Returns:
            验证通过返回序列号值
            
        Raises:
            ValidationError: 序列号已存在
        """
        instance = self.instance
        if Assets.objects.filter(serial_number=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError('序列号已存在')
        return value