from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='pos_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('user-management/', views.user_management, name='user_management'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    
    # Manager URLs
    path('product-management/', views.product_management, name='product_management'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('sales-reports/', views.sales_reports, name='sales_reports'),
    
    # Teller URLs
    path('pos-system/', views.pos_system, name='pos_system'),
    path('today-sales/', views.today_sales, name='today_sales'),
]