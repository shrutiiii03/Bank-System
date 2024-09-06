from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan, Customer, Transaction
from .serializers import LoanSerializer, TransactionSerializer, PaymentSerializer
from decimal import Decimal
from django.http import JsonResponse

def home(request):
    return render(request, 'bank_system/home.html')

def apply_for_loan(request):
    return render(request, 'bank_system/apply_for_loan.html')
@api_view(['POST'])
def lend_money(request):
    serializer = LoanSerializer(data=request.data)
    if serializer.is_valid():
        try:
            loan = serializer.save()
            total_amount = loan.total_amount
            emi_amount = loan.emi_amount

            response_data = {
                "total_amount": total_amount,  
                "emi_amount": emi_amount,
                'loan_id': loan.id,      
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "An unexpected error occurred while processing the loan."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def pay_loan(request):
    return render(request, 'bank_system/pay_loan.html')
@api_view(['POST'])
def make_payment(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        loan_id = serializer.validated_data['loan_id']
        payment_amount = Decimal(serializer.validated_data['payment_amount'])
        payment_type = serializer.validated_data['payment_type']

        try:
            loan = Loan.objects.get(id=loan_id)         
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
        if payment_amount > loan.total_amount:
            return Response({'error': 'Payment amount exceeds outstanding loan balance'}, status=status.HTTP_400_BAD_REQUEST)
        if payment_type == 'EMI':
            print("Processing EMI payment")  
            loan.total_amount -= loan.emi_amount 
            loan.emi_left -= 1  
            payment_amount=loan.emi_amount
        elif payment_type == 'LUMP_SUM':          
            loan.total_amount -= payment_amount   
        else:         
            return Response({'error': 'Invalid payment type'}, status=status.HTTP_400_BAD_REQUEST)
            
        loan.save()
        Transaction.objects.create(
            loan=loan,
            payment_amount=payment_amount,
            payment_type=payment_type
        )
        return Response({
            'message': 'Payment successful',
            'remaining_balance': loan.total_amount,
            'emi_left': loan.emi_left
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def ledger(request):
    return render(request, 'bank_system/ledger.html')
@api_view(['GET'])
def loan_ledger(request, loan_id):
    if not loan_id:
        return Response({'error': 'Loan ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        loan = Loan.objects.get(id=loan_id)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
    transactions = Transaction.objects.filter(loan=loan)
    serializer = TransactionSerializer(transactions, many=True)
    response_data = {
        'loan_id': loan_id,
        'balance_amount': loan.total_amount,
        'monthly_emi': loan.emi_amount,
        'emi_left': loan.emi_left,
        'transactions': serializer.data
    }
    return JsonResponse(response_data)
from django.db.models import Sum

def overview(request):
    return render(request, 'bank_system/overview.html')
@api_view(['GET'])
def account_overview(request, customer_id):
    if not customer_id:
        return Response({'error': 'Customer ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        customer = Customer.objects.get(customer_id=customer_id) 
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)
    loan_data = []
    for loan in loans:
        total_amount = loan.calculate_total_amount
        amount_paid = Transaction.objects.filter(loan=loan).aggregate(total_paid=Sum('payment_amount'))['total_paid'] or Decimal('0')
        emi_left = loan.loan_period - Transaction.objects.filter(loan=loan, payment_type='EMI').count()

        loan_data.append({
            'loan_id': loan.id,
            'loan_amount': loan.loan_amount,
            'total_amount': total_amount,
            'emi_amount': loan.calculate_emi,
            'total_interest': total_amount - loan.loan_amount,
            'amount_paid': amount_paid,
            'emi_left': emi_left
        })
    
    return JsonResponse({
        'customer_id': customer_id,
        'loans': loan_data
    })


