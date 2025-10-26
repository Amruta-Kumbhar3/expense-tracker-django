from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

CURRENCY_CHOICES = [
    ('MYR', 'MYR (RM)'),
    ('USD', 'USD ($)'),
    ('EUR', 'EUR (€)'),
    ('INR', 'INR (₹)'),
    ('SGD',  'SGD ($)'),
]

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Transport', 'Transport'),
        ('Shopping', 'Shopping'),
        ('Bills', 'Bills'),
        ('Entertainment', 'Entertainment'),
        ('Other','Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=False)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    currency = models.CharField(
    max_length=3,
    choices=CURRENCY_CHOICES,
    default='MYR'
)
    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"