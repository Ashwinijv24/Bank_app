from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from staff.views import CustomTokenObtainPairView, StaffViewSet
from customers.views import (CustomerViewSet, AccountViewSet, TransactionViewSet,
                              LoanViewSet, CreditCardViewSet, ReportViewSet,
                              CustomerRegisterView)

def api_root(request):
    return JsonResponse({
        'message': 'Rural Banking System API',
        'version': '1.0',
        'endpoints': {
            'login': '/api/login/',
            'customers': '/api/customers/',
            'accounts': '/api/accounts/',
            'transactions': '/api/transactions/',
            'loans': '/api/loans/',
            'credit-cards': '/api/credit-cards/',
            'reports': '/api/reports/dashboard/',
        },
        'frontend': 'https://enchanting-capybara-9efc5b.netlify.app',
        'backend': 'https://bank-app-3-1fn0.onrender.com',
        'admin': '/admin/',
    })

router = DefaultRouter()
router.register(r'staff', StaffViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'credit-cards', CreditCardViewSet)
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'register', CustomerRegisterView, basename='register')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]
