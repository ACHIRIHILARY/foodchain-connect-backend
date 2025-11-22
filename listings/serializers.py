from rest_framework import serializers
from .models import FoodListing

class FoodListingSerializer(serializers.ModelSerializer):
    provider_name = serializers.ReadOnlyField(source='provider.username')

    class Meta:
        model = FoodListing
        fields = '__all__'
        read_only_fields = ('provider', 'status', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['provider'] = self.context['request'].user
        return super().create(validated_data)
