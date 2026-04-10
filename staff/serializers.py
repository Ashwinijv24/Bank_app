from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

Staff = get_user_model()


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'employee_id', 'phone', 'address', 'is_active_staff']
        read_only_fields = ['id']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        branch = self.user.branch
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.get_full_name(),
            'employee_id': self.user.employee_id,
            'phone': self.user.phone,
            'address': self.user.address,
            'date_joined': self.user.date_joined.strftime('%d %b %Y') if self.user.date_joined else '',
            'branch': {
                'name': branch.name,
                'code': branch.code,
                'address': branch.address,
                'phone': branch.phone,
                'email': branch.email,
            } if branch else None,
        }
        return data
