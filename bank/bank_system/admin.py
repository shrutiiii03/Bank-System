from django.contrib import admin
from django.contrib import admin
from .models import Customer, Loan, Transaction

admin.site.register(Customer)
admin.site.register(Loan)
admin.site.register(Transaction)
