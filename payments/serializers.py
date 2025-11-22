from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, PaymentTransaction

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.ReadOnlyField(source='plan.name')

    class Meta:
        model = UserSubscription
        fields = '__all__'

class PaymentTransactionSerializer(serializers.ModelSerializer):
    plan_name = serializers.ReadOnlyField(source='plan.name')

    class Meta:
        model = PaymentTransaction
        fields = '__all__'

class InitiatePaymentSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50, required=False)
