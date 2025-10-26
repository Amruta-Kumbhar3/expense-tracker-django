from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'category', 'amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'id': 'id_date'}),
            'currency': forms.Select(attrs={'class': 'form-input'}),
        }
