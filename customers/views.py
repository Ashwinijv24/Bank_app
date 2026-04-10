from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
import random
from .models import Customer, Account, Transaction, Loan, CreditCard
from .serializers import (CustomerSerializer, AccountSerializer, TransactionSerializer,
                          LoanSerializer, CreditCardSerializer)


class PermissionMixin:
    """Mixin for role-based permissions"""
    
    def check_role(self, allowed_roles):
        return self.request.user.role in allowed_roles


class CustomerRegisterView(viewsets.ViewSet):
    """Public endpoint — customers self-register and login (no auth required)"""
    permission_classes = []

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save(created_by=None)

        # Auto-create a Savings account for the new customer
        account_number = f"ACC{customer.id:04d}{random.randint(100000, 999999)}"
        while Account.objects.filter(account_number=account_number).exists():
            account_number = f"ACC{customer.id:04d}{random.randint(100000, 999999)}"

        account = Account.objects.create(
            customer=customer,
            account_number=account_number,
            account_type='Savings',
            balance=0,
            status='Active',
        )

        return Response({
            'message': 'Registration successful',
            'data': serializer.data,
            'account_number': account.account_number,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Public customer login — verify by phone + aadhar"""
        phone = request.data.get('phone_number', '').strip()
        aadhar = request.data.get('aadhar_number', '').strip()
        if not phone or not aadhar:
            return Response({'error': 'Phone number and Aadhar number are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = Customer.objects.get(phone_number=phone, aadhar_number=aadhar)
            serializer = CustomerSerializer(customer)
            return Response({'message': 'Login successful', 'customer': serializer.data})
        except Customer.DoesNotExist:
            return Response({'error': 'No account found with these details. Please register first.'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Public customer dashboard — fetch all data by customer id"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        accounts = Account.objects.filter(customer=customer)
        loans = Loan.objects.filter(customer=customer)
        credit_cards = CreditCard.objects.filter(customer=customer)
        account_ids = accounts.values_list('id', flat=True)
        transactions = Transaction.objects.filter(account_id__in=account_ids).order_by('-timestamp')[:50]
        total_balance = sum(float(a.balance) for a in accounts)

        return Response({
            'customer': CustomerSerializer(customer).data,
            'accounts': AccountSerializer(accounts, many=True).data,
            'transactions': TransactionSerializer(transactions, many=True).data,
            'loans': LoanSerializer(loans, many=True).data,
            'credit_cards': CreditCardSerializer(credit_cards, many=True).data,
            'summary': {
                'total_balance': total_balance,
                'total_accounts': accounts.count(),
                'active_loans': loans.filter(status__in=['Pending', 'Approved', 'Active']).count(),
                'pending_loans': loans.filter(status='Pending').count(),
                'total_transactions': transactions.count(),
            }
        })

    @action(detail=False, methods=['post'])
    def apply_loan(self, request):
        """Public loan application by customer"""
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        loan_type = request.data.get('loan_type', 'personal')
        try:
            loan_amount = Decimal(str(request.data.get('loan_amount', 0)))
            tenure_months = int(request.data.get('tenure_months', 12))
            annual_income = Decimal(str(request.data.get('annual_income', 0)))
        except Exception:
            return Response({'error': 'Invalid numeric values'}, status=status.HTTP_400_BAD_REQUEST)

        interest_rates = {
            'personal': 5.0, 'auto': 3.5, 'home': 2.8,
            'business': 6.5, 'education': 4.2, 'emergency': 7.0,
        }
        interest_rate = Decimal(str(interest_rates.get(loan_type, 5.0)))

        loan = Loan.objects.create(
            customer=customer,
            loan_type=loan_type,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure_months=tenure_months,
            employment_status=request.data.get('employment_status', 'employed_full'),
            annual_income=annual_income,
            documents_submitted=request.data.get('purpose', ''),
            status='Pending',
        )

        return Response({
            'message': 'Loan application submitted! Status: Pending review by bank.',
            'loan_id': loan.id,
            'status': loan.status,
            'loan_type': loan.get_loan_type_display(),
            'loan_amount': str(loan.loan_amount),
            'monthly_payment': str(loan.monthly_payment),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """Customer self-deposit"""
        customer_id = request.data.get('customer_id')
        account_number = request.data.get('account_number', '').strip()
        try:
            amount = Decimal(str(request.data.get('amount', 0)))
        except Exception:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.select_for_update().get(
                account_number=account_number, customer_id=customer_id, status='Active')
        except Account.DoesNotExist:
            return Response({'error': 'Account not found or inactive'}, status=status.HTTP_404_NOT_FOUND)

        with db_transaction.atomic():
            account.balance += amount
            account.save()
            tx = Transaction.objects.create(
                account=account, transaction_type='DEPOSIT', amount=amount, created_by=None)

        return Response({'message': f'₹{amount} deposited successfully',
                         'new_balance': str(account.balance),
                         'transaction_id': tx.id})

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Customer self-withdrawal"""
        customer_id = request.data.get('customer_id')
        account_number = request.data.get('account_number', '').strip()
        try:
            amount = Decimal(str(request.data.get('amount', 0)))
        except Exception:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.select_for_update().get(
                account_number=account_number, customer_id=customer_id, status='Active')
        except Account.DoesNotExist:
            return Response({'error': 'Account not found or inactive'}, status=status.HTTP_404_NOT_FOUND)

        if account.balance < amount:
            return Response({'error': f'Insufficient balance. Available: ₹{account.balance}'},
                            status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            account.balance -= amount
            account.save()
            tx = Transaction.objects.create(
                account=account, transaction_type='WITHDRAW', amount=amount, created_by=None)

        return Response({'message': f'₹{amount} withdrawn successfully',
                         'new_balance': str(account.balance),
                         'transaction_id': tx.id})

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """Customer self-transfer"""
        customer_id = request.data.get('customer_id')
        from_account_number = request.data.get('from_account', '').strip()
        to_account_number = request.data.get('to_account', '').strip()
        try:
            amount = Decimal(str(request.data.get('amount', 0)))
        except Exception:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)
        if from_account_number == to_account_number:
            return Response({'error': 'Cannot transfer to the same account'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_acc = Account.objects.select_for_update().get(
                account_number=from_account_number, customer_id=customer_id, status='Active')
        except Account.DoesNotExist:
            return Response({'error': 'Source account not found or inactive'}, status=status.HTTP_404_NOT_FOUND)

        try:
            to_acc = Account.objects.select_for_update().get(account_number=to_account_number, status='Active')
        except Account.DoesNotExist:
            return Response({'error': 'Destination account not found or inactive'}, status=status.HTTP_404_NOT_FOUND)

        if from_acc.balance < amount:
            return Response({'error': f'Insufficient balance. Available: ₹{from_acc.balance}'},
                            status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            from_acc.balance -= amount
            to_acc.balance += amount
            from_acc.save()
            to_acc.save()
            Transaction.objects.create(account=from_acc, transaction_type='TRANSFER',
                                       amount=amount, reference_account=to_account_number, created_by=None)
            Transaction.objects.create(account=to_acc, transaction_type='TRANSFER',
                                       amount=amount, reference_account=from_account_number, created_by=None)

        return Response({'message': f'₹{amount} transferred successfully to {to_account_number}',
                         'new_balance': str(from_acc.balance)})


class CustomerViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Customer.objects.all()
    
    def create(self, request, *args, **kwargs):
        if not self.check_role(['FIELD', 'CSE']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        # Only Field Officer and CSE can update customers
        if not self.check_role(['FIELD', 'CSE']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class AccountViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Generate unique account number
        account_number = f"ACC{random.randint(1000000000, 9999999999)}"
        while Account.objects.filter(account_number=account_number).exists():
            account_number = f"ACC{random.randint(1000000000, 9999999999)}"
        
        data = request.data.copy()
        data['account_number'] = account_number
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        account_id = self.request.query_params.get('account_id')
        if account_id:
            return Transaction.objects.filter(account_id=account_id)
        return Transaction.objects.all()
    
    @action(detail=False, methods=['post'])
    def deposit(self, request):
        # Only CSE can perform deposits
        if not self.check_role(['CSE']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        account_number = request.data.get('account_number')
        amount = Decimal(str(request.data.get('amount', 0)))
        
        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with db_transaction.atomic():
                account = Account.objects.select_for_update().get(account_number=account_number)
                account.balance += amount
                account.save()
                
                transaction = Transaction.objects.create(
                    account=account,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    created_by=request.user
                )
                
                serializer = TransactionSerializer(transaction)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        # Only CSE can perform withdrawals
        if not self.check_role(['CSE']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        account_number = request.data.get('account_number')
        amount = Decimal(str(request.data.get('amount', 0)))
        
        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with db_transaction.atomic():
                account = Account.objects.select_for_update().get(account_number=account_number)
                
                if account.balance < amount:
                    return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
                
                account.balance -= amount
                account.save()
                
                transaction = Transaction.objects.create(
                    account=account,
                    transaction_type='WITHDRAW',
                    amount=amount,
                    created_by=request.user
                )
                
                serializer = TransactionSerializer(transaction)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def transfer(self, request):
        # Only CSE can perform transfers
        if not self.check_role(['CSE']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from_account_number = request.data.get('from_account')
        to_account_number = request.data.get('to_account')
        amount = Decimal(str(request.data.get('amount', 0)))
        
        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with db_transaction.atomic():
                from_account = Account.objects.select_for_update().get(account_number=from_account_number)
                to_account = Account.objects.select_for_update().get(account_number=to_account_number)
                
                if from_account.balance < amount:
                    return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
                
                from_account.balance -= amount
                to_account.balance += amount
                from_account.save()
                to_account.save()
                
                # Create debit transaction
                Transaction.objects.create(
                    account=from_account,
                    transaction_type='TRANSFER',
                    amount=amount,
                    reference_account=to_account_number,
                    created_by=request.user
                )
                
                # Create credit transaction
                transaction = Transaction.objects.create(
                    account=to_account,
                    transaction_type='TRANSFER',
                    amount=amount,
                    reference_account=from_account_number,
                    created_by=request.user
                )
                
                return Response({'message': 'Transfer successful'}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


class LoanViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Only Loan Officer can create loans
        if not self.check_role(['LOAN']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate employment and income
        employment_status = request.data.get('employment_status')
        annual_income = float(request.data.get('annual_income', 0))
        loan_type = request.data.get('loan_type', 'personal')
        loan_amount = float(request.data.get('loan_amount', 0))
        
        # Special rules for unemployed
        if employment_status == 'unemployed':
            if loan_type != 'emergency':
                return Response({
                    'error': 'Unemployed applicants can only apply for emergency loans'
                }, status=status.HTTP_400_BAD_REQUEST)
            if loan_amount > 5000:
                return Response({
                    'error': 'Emergency loans for unemployed are limited to $5,000'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Minimum income requirement
            if annual_income < 25000:
                return Response({
                    'error': 'Minimum annual income of $25,000 required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate loan amount limits by type
        loan_limits = {
            'personal': (1000, 100000),
            'home': (5000, 500000),
            'auto': (1000, 50000),
            'education': (500, 200000),
            'business': (1000, 100000),
            'emergency': (100, 20000),
        }
        
        min_amount, max_amount = loan_limits.get(loan_type, (1000, 100000))
        if loan_amount < min_amount or loan_amount > max_amount:
            return Response({
                'error': f'{loan_type.title()} loan amount must be between ${min_amount:,.0f} and ${max_amount:,.0f}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set interest rate based on loan type
        interest_rates = {
            'personal': 5.0,
            'auto': 3.5,
            'home': 2.8,
            'business': 6.5,
            'education': 4.2,
            'emergency': 7.0,
        }
        
        data = request.data.copy()
        data['interest_rate'] = interest_rates.get(loan_type, 5.0)
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        # Only Manager can approve loans
        if not self.check_role(['MANAGER']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        loan = self.get_object()
        if loan.status != 'Pending':
            return Response({'error': 'Loan is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        loan.status = 'Approved'
        loan.approved_by = request.user
        loan.approval_date = timezone.now()
        loan.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        # Only Manager can reject loans
        if not self.check_role(['MANAGER']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        loan = self.get_object()
        if loan.status != 'Pending':
            return Response({'error': 'Loan is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        loan.status = 'Rejected'
        loan.rejection_reason = request.data.get('reason', 'Not specified')
        loan.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def loan_types(self, request):
        """Get available loan types with their details"""
        loan_types = [
            {
                'type': 'personal',
                'name': 'Personal Loan',
                'interest_rate': 5.0,
                'min_amount': 1000,
                'max_amount': 100000,
                'description': 'For personal expenses and emergencies'
            },
            {
                'type': 'auto',
                'name': 'Auto Loan',
                'interest_rate': 3.5,
                'min_amount': 1000,
                'max_amount': 50000,
                'description': 'For purchasing vehicles'
            },
            {
                'type': 'home',
                'name': 'Home Loan',
                'interest_rate': 2.8,
                'min_amount': 5000,
                'max_amount': 500000,
                'description': 'For purchasing or renovating homes'
            },
            {
                'type': 'business',
                'name': 'Business Loan',
                'interest_rate': 6.5,
                'min_amount': 1000,
                'max_amount': 100000,
                'description': 'For business expansion and operations'
            },
            {
                'type': 'education',
                'name': 'Education Loan',
                'interest_rate': 4.2,
                'min_amount': 500,
                'max_amount': 200000,
                'description': 'For educational expenses'
            },
            {
                'type': 'emergency',
                'name': 'Emergency Loan',
                'interest_rate': 7.0,
                'min_amount': 100,
                'max_amount': 20000,
                'description': 'For urgent financial needs'
            },
        ]
        return Response(loan_types)
    
    @action(detail=False, methods=['post'])
    def calculate_emi(self, request):
        """Calculate EMI for given loan parameters"""
        import math
        from decimal import Decimal
        
        try:
            loan_amount = float(request.data.get('loan_amount', 0))
            interest_rate = float(request.data.get('interest_rate', 0))
            tenure_months = int(request.data.get('tenure_months', 12))
            
            # Calculate EMI
            P = loan_amount
            annual_rate = interest_rate / 100
            r = annual_rate / 12
            n = tenure_months
            
            if r == 0:
                emi = P / n
            else:
                emi = P * r * math.pow(1 + r, n) / (math.pow(1 + r, n) - 1)
            
            total_payable = emi * n
            total_interest = total_payable - loan_amount
            
            # Calculate fees
            processing_fee = loan_amount * 0.02  # 2%
            gst = processing_fee * 0.18  # 18%
            net_disbursal = loan_amount - processing_fee - gst
            
            return Response({
                'monthly_emi': round(emi, 2),
                'total_interest': round(total_interest, 2),
                'total_payable': round(total_payable, 2),
                'processing_fee': round(processing_fee, 2),
                'gst_amount': round(gst, 2),
                'net_disbursal': round(net_disbursal, 2),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreditCardViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Only CSE can request credit cards
        if not self.check_role(['CSE']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Generate unique card number
        card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        while CreditCard.objects.filter(card_number=card_number).exists():
            card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        
        data = request.data.copy()
        data['card_number'] = card_number
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        # Only Manager can approve credit cards
        if not self.check_role(['MANAGER']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        card = self.get_object()
        if card.status != 'Pending':
            return Response({'error': 'Card is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        card.status = 'Approved'
        card.approved_by = request.user
        card.save()
        
        serializer = self.get_serializer(card)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def customer(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cards = CreditCard.objects.filter(customer_id=customer_id)
        serializer = self.get_serializer(cards, many=True)
        return Response(serializer.data)


class ReportViewSet(PermissionMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        # Only Manager can view reports
        if not self.check_role(['MANAGER']):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        today = timezone.now().date()
        
        data = {
            'total_customers': Customer.objects.count(),
            'total_accounts': Account.objects.count(),
            'total_loans': Loan.objects.count(),
            'total_transactions_today': Transaction.objects.filter(timestamp__date=today).count(),
            'pending_loans': Loan.objects.filter(status='Pending').count(),
            'approved_loans': Loan.objects.filter(status='Approved').count(),
            'total_deposits_today': Transaction.objects.filter(
                timestamp__date=today, 
                transaction_type='DEPOSIT'
            ).aggregate(total=Sum('amount'))['total'] or 0,
        }
        
        return Response(data)
