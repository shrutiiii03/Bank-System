from django.db import models
from decimal import Decimal

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Loan(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_period = models.IntegerField()
    rate_of_interest = models.DecimalField(max_digits=5, decimal_places=2)  # Changed to Decimal
    total_amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    emi_amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    emi_left = models.IntegerField()
    loan_taken_date = models.DateTimeField(auto_now_add=True)

    @property
    def calculate_interest(self):
        loan_amount = Decimal(self.loan_amount)
        loan_period = Decimal(self.loan_period)
        rate_of_interest = Decimal(self.rate_of_interest)
        return loan_amount * (loan_period / Decimal('12')) * rate_of_interest / Decimal('100')

    @property
    def calculate_total_amount(self):
        return self.loan_amount + self.calculate_interest

    @property
    def calculate_emi(self):
        loan_amount = Decimal(self.loan_amount)
        monthly_rate = Decimal(self.rate_of_interest) / (Decimal('12') * Decimal('100'))
        emi = loan_amount * monthly_rate * (1 + monthly_rate) ** Decimal(self.loan_period) / \
            ((1 + monthly_rate) ** Decimal(self.loan_period) - 1)
        return round(emi, 2)

    def save(self, *args, **kwargs):
        if self.total_amount is None:
            self.total_amount = self.calculate_total_amount
        if self.emi_amount is None:
            self.emi_amount = self.calculate_emi
        super().save(*args, **kwargs)

class Transaction(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=10)  # EMI or LUMP SUM

    def __str__(self):
        return f"Transaction for Loan ID {self.loan.id}"
