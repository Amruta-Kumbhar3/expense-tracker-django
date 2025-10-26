from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Expense, CURRENCY_CHOICES
from django.conf import settings
from .forms import ExpenseForm
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64


API_KEY = '13cb1ae77ad7a4c771a51821'

# Home page (requires login)
@login_required
def home(request):
    expenses = Expense.objects.all()
    selected_currency = request.GET.get('currency', 'MYR')
    converted_expenses = {}

    for exp in expenses:
        if selected_currency != 'MYR':
            try:
                # Make API call
                API_KEY = "13cb1ae77ad7a4c771a51821"
                url = f"https://v6.exchangerate-api.com/v6/13cb1ae77ad7a4c771a51821/pair/MYR/{selected_currency}/{exp.amount}"
                response = requests.get(url, timeout=10)

                # Only parse JSON if response is valid
                if response.status_code == 200:
                    data = response.json()
                    if data.get('result') == 'success':
                        converted_expenses[exp.id] = data['conversion_result']
                    else:
                        converted_expenses[exp.id] = exp.amount
                else:
                    converted_expenses[exp.id] = exp.amount

            except Exception as e:
                print(f"Currency conversion failed for {exp.id}: {e}")
                converted_expenses[exp.id] = exp.amount
        else:
            converted_expenses[exp.id] = exp.amount

    context = {
        'expenses': expenses,
        'selected_currency': selected_currency,
        'converted_expenses': converted_expenses,
    }
    return render(request, 'expense_tracker/home.html', context)

def get_exchange_rate(base="MYR", target="USD"):
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
    response = requests.get(url)
    data = response.json()
    rate = data["conversion_rates"].get(target)
    return rate

def expense_chart(request):
    # Your logic for categories (example)
    categories = {
        "Food": 1200,
        "Transport": 10,
        "Shopping": 100
    }

    # Detect dark mode from query parameter
    dark_mode = request.GET.get('theme') == 'dark'

    # Apply theme style
    plt.style.use('dark_background' if dark_mode else 'default')
    plt.figure(figsize=(6, 4))

    wedges, texts, autotexts = plt.pie(
        categories.values(),
        labels=categories.keys(),
        autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
        startangle=90,
        colors=plt.cm.Set3.colors,
        wedgeprops={'width': 0.4, 'edgecolor': 'white'},
        pctdistance=0.8,
        labeldistance=1.1
    )

    # Adjust text colors based on theme
    text_color = 'white' if dark_mode else 'black'
    plt.setp(autotexts, size=10, weight="bold", color=text_color)
    plt.setp(texts, size=9, color=text_color)
    plt.title('Expenses by Category (Donut)', color=text_color, fontsize=12, fontweight='bold')

    # Center total
    plt.text(
        0, 0,
        f"Total\n{sum(categories.values())}",
        ha='center',
        va='center',
        fontsize=12,
        fontweight='bold',
        color=text_color
    )

    plt.tight_layout()

    # Convert to image
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return render(request, 'expense_tracker/chart.html', {'chart': image_base64})

# Register page
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please log in.")
            return redirect("register")

        # Create new user
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Registered successfully! You can now log in.")
        return redirect("login")

    return render(request, "expense_tracker/register.html")

# Login page
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "expense_tracker/login.html")

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # assign logged-in user
            expense.save()               # created_at is automatically set
            return redirect('home')
    else:
        form = ExpenseForm()
    
    return render(request, 'expense_tracker/add_expense.html', {'form': form})



def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return redirect('home')
    
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home or your expense list page
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'expense_tracker/edit_expense.html', {'form': form, 'expense': expense})