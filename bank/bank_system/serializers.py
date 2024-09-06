from rest_framework import serializers
from .models import Loan, Customer, Transaction

class LoanSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True, required=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    emi_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = ['customer_id', 'loan_amount', 'loan_period', 'rate_of_interest', 'total_amount', 'emi_amount']

    def create(self, validated_data):
        customer_id = validated_data.get('customer_id')

        if not customer_id:
            raise serializers.ValidationError('Customer ID is required')

        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
            raise serializers.ValidationError('Customer with this ID does not exist')

        loan_amount = validated_data['loan_amount']
        loan_period = validated_data['loan_period']
        rate_of_interest = validated_data['rate_of_interest']

        loan = Loan(
            customer=customer,
            loan_amount=loan_amount,
            loan_period=loan_period,
            rate_of_interest=rate_of_interest,
            emi_left=loan_period
        )
        loan.save()  # This will automatically calculate total_amount and emi_amount

        return loan


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['payment_amount', 'payment_date', 'payment_type']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name']

class PaymentSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_type = serializers.ChoiceField(choices=['EMI', 'LUMP_SUM'])
