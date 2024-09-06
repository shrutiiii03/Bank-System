from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply-for-loan/', views.apply_for_loan, name='apply_for_loan_page'),  # Home page
    path('lend/', views.lend_money, name='lend_money'),
    path('pay-loan/', views.pay_loan, name='pay_loan'),
    path('payment/', views.make_payment, name='make_payment'),
    path('ledger/', views.ledger, name='ledger'),
    path('ledger/<int:loan_id>/', views.loan_ledger, name='loan_ledger'),
    path('overview/', views.overview, name='overview'),
    path('account-overview/<int:customer_id>/', views.account_overview, name='account_overview'),
]
