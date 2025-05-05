from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm
from apps.accounts.models import PerfilUsuario
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from apps.productservice.models import Producto, Servicio, Pedido
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.context_processors import request
from django.db.models import Q

# Context processor que agrega el perfil de usuario autenticado a todos los templates.
def user_profile_context(request):
    """Context processor para agregar el perfil de usuario a todos los templates."""
    if request.user.is_authenticated:
        try:
            return {'user_profile': request.user.userprofile}
        except PerfilUsuario.DoesNotExist:
            return {'user_profile': None}
    return {'user_profile': None}

# Vista de registro de usuario. Muestra y procesa el formulario de registro.
def register(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'accounts/register.html', {'form': form})

# Vista principal (dashboard) del usuario autenticado. Muestra resumen de productos, servicios y pedidos recientes.
@login_required(login_url='login')
def home(request):
    perfil = PerfilUsuario.objects.select_related('usuario').get(usuario=request.user)
    productos = Producto.objects.filter(usuario=request.user).prefetch_related('imagenes')
    servicios = Servicio.objects.filter(usuario=request.user).prefetch_related('imagenes')
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')[:5]
    
    # Debug
    print(f"Debug - Usuario: {request.user.username}")
    print(f"Debug - Is Admin: {perfil.is_admin}")
    print(f"Debug - Tipo de is_admin: {type(perfil.is_admin)}")
    
    context = {
        'perfil': perfil,
        'productos': productos,
        'servicios': servicios,
        'pedidos': pedidos,
        'user': request.user,  # Asegurarnos que el usuario está en el contexto
    }
    return render(request, 'accounts/home.html', context)

# Vista para cerrar sesión del usuario.
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

# Vista de perfil del usuario autenticado. Permite ver y editar datos personales.
@login_required(login_url='login')
def perfil(request):
    perfil = PerfilUsuario.objects.get(usuario=request.user)
    if request.method == 'POST':
        # Aquí irá la lógica para actualizar el perfil
        pass
    return render(request, 'accounts/perfil.html', {'perfil': perfil})

# Vista de login personalizada. Muestra y procesa el formulario de autenticación.
@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, '¡Has iniciado sesión correctamente!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Vista landing pública (página de inicio para usuarios no autenticados).
def landing(request):
    return render(request, 'landing.html')

# Vista del dashboard de administración. Solo accesible para administradores. Muestra métricas globales.
@login_required(login_url='login')
def admin_dashboard(request):
    if request.user.userprofile.permisos != 'Administrador':
        messages.error(request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('home')
    
    total_users = User.objects.count()
    total_admins = User.objects.filter(userprofile__permisos='Administrador').count()
    
    return render(request, 'accounts/admin/dashboard.html', {
        'total_users': total_users,
        'total_admins': total_admins
    })

# Vista para gestionar usuarios (listar, buscar, paginar). Solo para administradores.
@login_required(login_url='login')
def manage_users(request):
    if request.user.userprofile.permisos != 'Administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    users = User.objects.select_related('userprofile').all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(userprofile__empresa__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'accounts/admin/manage_users.html', {
        'users': users
    })

# Vista de detalle y edición de un usuario específico. Solo para administradores.
@login_required(login_url='login')
def user_detail(request, user_id):
    if request.user.userprofile.permisos != 'Administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    user_detail = get_object_or_404(User.objects.select_related('userprofile'), id=user_id)
    
    if request.method == 'POST':
        user_detail.username = request.POST.get('username')
        user_detail.email = request.POST.get('email')
        user_detail.is_active = request.POST.get('is_active') == 'on'
        user_detail.save()
        
        user_detail.userprofile.empresa = request.POST.get('empresa')
        user_detail.userprofile.telefono = request.POST.get('telefono')
        user_detail.userprofile.direccion = request.POST.get('direccion')
        user_detail.userprofile.permisos = request.POST.get('permisos', 'Usuario')
        user_detail.userprofile.save()
        
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('manage_users')
    
    return render(request, 'accounts/admin/user_detail.html', {
        'user_detail': user_detail
    })

# Vista para ver los productos de un usuario específico. Solo para administradores.
@login_required(login_url='login')
def admin_products(request, user_id):
    if request.user.userprofile.permisos != 'Administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    user_detail = get_object_or_404(User, id=user_id)
    products = Producto.objects.filter(usuario=user_detail).prefetch_related('imagenes')
    
    return render(request, 'accounts/admin/user_products.html', {
        'user_detail': user_detail,
        'products': products
    })

# Vista para ver los servicios de un usuario específico. Solo para administradores.
@login_required(login_url='login')
def admin_services(request, user_id):
    if request.user.userprofile.permisos != 'Administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    user_detail = get_object_or_404(User, id=user_id)
    services = Servicio.objects.filter(usuario=user_detail).prefetch_related('imagenes')
    
    return render(request, 'accounts/admin/user_services.html', {
        'user_detail': user_detail,
        'services': services
    })

# Vista para ver los pedidos de un usuario específico, con filtros y paginación. Solo para administradores.
@login_required(login_url='login')
def admin_orders(request, user_id):
    if not request.user.userprofile.is_admin:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    user_detail = get_object_or_404(User, id=user_id)
    orders = Pedido.objects.filter(usuario=user_detail)
    
    # Filtros
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        orders = orders.filter(estado=status)
    if date_from:
        orders = orders.filter(fecha_creacion__gte=date_from)
    if date_to:
        orders = orders.filter(fecha_creacion__lte=date_to)
    
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    return render(request, 'accounts/admin/user_orders.html', {
        'user_detail': user_detail,
        'orders': orders
    })

# Vista para activar/desactivar usuarios vía AJAX. Solo para administradores.
@login_required(login_url='login')
@require_POST
def toggle_user_status(request):
    if not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'No tienes permisos para realizar esta acción.'}, status=403)
    
    user_id = request.POST.get('user_id')
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'is_active': user.is_active
    })
