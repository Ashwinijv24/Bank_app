from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CreditCardApplication
from .serializers import CreditCardApplicationSerializer

class CreditCardApplicationViewSet(viewsets.ModelViewSet):
    queryset = CreditCardApplication.objects.all()
    serializer_class = CreditCardApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return CreditCardApplication.objects.all()
        elif user.role == 'clerk':
            return CreditCardApplication.objects.filter(status='pending')
        elif user.role == 'auditor':
            return CreditCardApplication.objects.all()
        return CreditCardApplication.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.role not in ['manager', 'clerk']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        application = self.get_object()
        application.status = 'approved'
        application.processed_by = request.user
        application.remarks = request.data.get('remarks', '')
        application.save()
        
        return Response(CreditCardApplicationSerializer(application).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if request.user.role not in ['manager', 'clerk']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        application = self.get_object()
        application.status = 'rejected'
        application.processed_by = request.user
        application.remarks = request.data.get('remarks', '')
        application.save()
        
        return Response(CreditCardApplicationSerializer(application).data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        if request.user.role != 'manager':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total = CreditCardApplication.objects.count()
        approved = CreditCardApplication.objects.filter(status='approved').count()
        rejected = CreditCardApplication.objects.filter(status='rejected').count()
        pending = CreditCardApplication.objects.filter(status='pending').count()
        
        return Response({
            'total': total,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
        })
