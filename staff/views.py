from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import StaffSerializer, CustomTokenObtainPairSerializer

Staff = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from customers.models import Customer, Account, Loan, Transaction, CreditCard
        from django.utils import timezone
        today = timezone.now().date()
        return Response({
            'total_customers': Customer.objects.count(),
            'total_accounts': Account.objects.count(),
            'total_loans': Loan.objects.count(),
            'pending_loans': Loan.objects.filter(status='Pending').count(),
            'approved_loans': Loan.objects.filter(status='Approved').count(),
            'total_staff': Staff.objects.count(),
            'transactions_today': Transaction.objects.filter(timestamp__date=today).count(),
            'pending_credit_cards': CreditCard.objects.filter(status='Pending').count(),
        })
