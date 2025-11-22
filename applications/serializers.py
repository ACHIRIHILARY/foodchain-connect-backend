from rest_framework import serializers
from .models import FoodApplication

class FoodApplicationSerializer(serializers.ModelSerializer):
    seeker_name = serializers.ReadOnlyField(source='seeker.username')
    listing_title = serializers.ReadOnlyField(source='listing.title')

    class Meta:
        model = FoodApplication
        fields = '__all__'
        read_only_fields = ('seeker', 'status', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['seeker'] = self.context['request'].user
        return super().create(validated_data)
