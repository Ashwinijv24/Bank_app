from rest_framework import serializers
from .models import CreditCardApplication

class CreditCardApplicationSerializer(serializers.ModelSerializer):
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = CreditCardApplication
        fields = [
            'id', 'applicant_name', 'applicant_email', 'applicant_phone',
            'salary', 'currency', 'card_type', 'status', 'processed_by',
            'processed_by_name', 'created_at', 'updated_at', 'remarks'
        ]
        read_only_fields = ['id', 'processed_by', 'created_at', 'updated_at']
