from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),  # Página de inicio pública
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),  # Login de usuario
    path('logout/', views.logout_view, name='logout'),  # Logout de usuario
    path('register/', views.register, name='register'),  # Registro de usuario
    path('home/', views.home, name='home'),  # Dashboard del usuario autenticado
    path('perfil/', views.perfil, name='perfil'),  # Perfil del usuario
    
    # URLs del panel de administración
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Dashboard de admin
    path('dashboard/users/', views.manage_users, name='manage_users'),  # Gestión de usuarios
    path('dashboard/users/<int:user_id>/', views.user_detail, name='user_detail'),  # Detalle de usuario
    path('dashboard/users/<int:user_id>/products/', views.admin_products, name='admin_products'),  # Productos de usuario
    path('dashboard/users/<int:user_id>/services/', views.admin_services, name='admin_services'),  # Servicios de usuario
    path('dashboard/users/<int:user_id>/orders/', views.admin_orders, name='admin_orders'),  # Pedidos de usuario
    path('dashboard/toggle-user-status/', views.toggle_user_status, name='toggle_user_status'),  # Activar/desactivar usuario
    
    # URLs de recuperación de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
] 