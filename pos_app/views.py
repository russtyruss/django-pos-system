from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Profile, Product, Transaction, TransactionItem
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ProductForm, TransactionForm, TransactionItemForm
from django.contrib.auth.models import User

def role_check(role):
    def check(user):
        try:
            return user.profile.role == role
        except Profile.DoesNotExist:
            return False
    return check

admin_required = user_passes_test(role_check('admin'))
manager_required = user_passes_test(role_check('manager'))
teller_required = user_passes_test(role_check('teller'))

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                role=form.cleaned_data.get('role')
            )
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'pos_app/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    if user.profile.role == 'admin':
        # Admin dashboard
        total_users = User.objects.count()
        active_users = User.objects.filter(profile__is_active=True).count()
        context.update({
            'total_users': total_users,
            'active_users': active_users,
        })
    
    elif user.profile.role == 'manager':
        # Manager dashboard
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        daily_sales = Transaction.objects.filter(
            transaction_date__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        weekly_sales = Transaction.objects.filter(
            transaction_date__date__gte=week_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_sales = Transaction.objects.filter(
            transaction_date__date__gte=month_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        total_sales = Transaction.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        
        context.update({
            'daily_sales': daily_sales,
            'weekly_sales': weekly_sales,
            'monthly_sales': monthly_sales,
            'total_sales': total_sales,
        })
    
    elif user.profile.role == 'teller':
        # Teller dashboard
        today = timezone.now().date()
        today_sales = Transaction.objects.filter(
            teller=user,
            transaction_date__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        today_transactions = Transaction.objects.filter(
            teller=user,
            transaction_date__date=today
        ).count()
        
        context.update({
            'today_sales': today_sales,
            'today_transactions': today_transactions,
        })
    
    return render(request, 'pos_app/dashboard.html', context)

@login_required
@admin_required
def user_management(request):
    users = User.objects.all()
    return render(request, 'pos_app/user_management.html', {'users': users})

@login_required
@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_management')
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)
    
    return render(request, 'pos_app/edit_user.html', {
        'u_form': u_form,
        'p_form': p_form
    })

@login_required
@manager_required
def product_management(request):
    products = Product.objects.all()
    return render(request, 'pos_app/product_management.html', {'products': products})

@login_required
@manager_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_management')
    else:
        form = ProductForm()
    
    return render(request, 'pos_app/add_product.html', {'form': form})

@login_required
@manager_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'pos_app/edit_product.html', {'form': form})

@login_required
@teller_required
def pos_system(request):
    products = Product.objects.filter(status='available')
    
    if request.method == 'POST':
        transaction_form = TransactionForm(request.POST)
        
        if transaction_form.is_valid():
            transaction = transaction_form.save(commit=False)
            transaction.teller = request.user
            
            # Calculate total amount from items
            total_amount = 0
            items = []
            
            for key, value in request.POST.items():
                if key.startswith('product_'):
                    product_id = key.split('_')[1]
                    quantity = int(value)
                    
                    if quantity > 0:
                        product = Product.objects.get(id=product_id)
                        item_total = product.price * quantity
                        total_amount += item_total
                        
                        items.append({
                            'product': product,
                            'quantity': quantity,
                            'price': product.price
                        })
            
            transaction.total_amount = total_amount
            transaction.save()
            
            # Save transaction items
            for item in items:
                TransactionItem.objects.create(
                    transaction=transaction,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )
            
            messages.success(request, f'Transaction completed successfully! Total: ${total_amount}')
            return redirect('pos_system')
    else:
        transaction_form = TransactionForm()
    
    return render(request, 'pos_app/pos_system.html', {
        'products': products,
        'form': transaction_form
    })

@login_required
@teller_required
def today_sales(request):
    today = timezone.now().date()
    transactions = Transaction.objects.filter(
        teller=request.user,
        transaction_date__date=today
    )
    
    return render(request, 'pos_app/today_sales.html', {'transactions': transactions})

@login_required
@manager_required
def sales_reports(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Daily sales
    daily_sales = Transaction.objects.filter(
        transaction_date__date=today
    ).values('teller__username').annotate(
        total_sales=Sum('total_amount'),
        transaction_count=Count('id')
    )
    
    # Weekly sales
    weekly_sales = Transaction.objects.filter(
        transaction_date__date__gte=week_ago
    ).values('teller__username').annotate(
        total_sales=Sum('total_amount'),
        transaction_count=Count('id')
    )
    
    # Monthly sales
    monthly_sales = Transaction.objects.filter(
        transaction_date__date__gte=month_ago
    ).values('teller__username').annotate(
        total_sales=Sum('total_amount'),
        transaction_count=Count('id')
    )
    
    # All-time sales
    all_time_sales = Transaction.objects.values('teller__username').annotate(
        total_sales=Sum('total_amount'),
        transaction_count=Count('id')
    )
    
    context = {
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'all_time_sales': all_time_sales,
    }

    return render(request, 'pos_app/sales_reports.html', context)