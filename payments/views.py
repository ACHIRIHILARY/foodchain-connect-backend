from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import SubscriptionPlan, UserSubscription, PaymentTransaction
from .serializers import (
    SubscriptionPlanSerializer, 
    UserSubscriptionSerializer, 
    PaymentTransactionSerializer,
    InitiatePaymentSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class PlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
            except SubscriptionPlan.DoesNotExist:
                return Response({'error': 'Plan not found'}, status=404)

            # Create Pending Transaction
            transaction = PaymentTransaction.objects.create(
                user=request.user,
                plan=plan,
                amount=plan.price,
                status=PaymentTransaction.Status.PENDING,
                provider_ref=str(uuid.uuid4()) # Mocking a provider reference
            )

            # Mock Payment URL
            payment_url = f"http://localhost:8000/api/payments/mock_gateway/{transaction.provider_ref}/"

            return Response({
                'transaction_id': transaction.id,
                'payment_url': payment_url,
                'message': 'Payment initiated. Use the payment_url to simulate payment completion.'
            })
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def webhook(self, request):
        # Mock Webhook to handle payment success
        # In real scenario, verify signature from Stripe/Flutterwave
        provider_ref = request.data.get('provider_ref')
        status_update = request.data.get('status')

        if not provider_ref or not status_update:
            return Response({'error': 'Invalid data'}, status=400)

        try:
            transaction = PaymentTransaction.objects.get(provider_ref=provider_ref)
        except PaymentTransaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=404)

        if status_update == 'SUCCESS':
            transaction.status = PaymentTransaction.Status.SUCCESS
            transaction.save()

            # Activate Subscription
            plan = transaction.plan
            end_date = timezone.now() + timedelta(days=plan.duration_days)
            
            UserSubscription.objects.update_or_create(
                user=transaction.user,
                defaults={
                    'plan': plan,
                    'end_date': end_date,
                    'is_active': True
                }
            )
            return Response({'status': 'Subscription activated'})
        
        transaction.status = PaymentTransaction.Status.FAILED
        transaction.save()
        return Response({'status': 'Payment failed recorded'})

    @action(detail=False, methods=['get'])
    def history(self, request):
        transactions = PaymentTransaction.objects.filter(user=request.user)
        serializer = PaymentTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mock_gateway/(?P<ref>[^/.]+)')
    def mock_gateway(self, request, ref=None):
        # Simple GET endpoint to simulate the payment page
        # In a real app, this would be hosted by Stripe/Flutterwave
        return Response({
            'message': 'This is a mock payment page.',
            'action': 'Send a POST request to /api/payments/webhook/ with {"provider_ref": "' + ref + '", "status": "SUCCESS"} to complete payment.'
        })
