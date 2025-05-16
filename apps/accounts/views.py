from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm, LandingPageForm
from apps.accounts.models import PerfilUsuario, LandingPage
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from apps.productservice.models import Producto, Servicio, Pedido
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.template.context_processors import request
from django.db.models import Q
from decimal import Decimal

# Context processor que agrega el perfil de usuario autenticado a todos los templates.
def user_profile_context(request):
    """Context processor para agregar perfil de usuario y datos de carrito a todos los templates."""
    context = {}
    # Perfil de usuario
    if request.user.is_authenticated:
        try:
            context['user_profile'] = request.user.userprofile
        except PerfilUsuario.DoesNotExist:
            context['user_profile'] = None
    else:
        context['user_profile'] = None
    # Carrito desde sesión
    cart_session = request.session.get('cart', {})
    # Contador total de items
    total_count = sum(cart_session.values()) if isinstance(cart_session, dict) else 0
    context['cart_count'] = total_count
    # Preview de primeros 3 productos
    cart_preview = []
    if total_count and isinstance(cart_session, dict):
        for prod_id, qty in list(cart_session.items())[:3]:
            try:
                producto = Producto.objects.get(pk=int(prod_id))
                cart_preview.append({'producto': producto, 'cantidad': qty})
            except Exception:
                continue
    context['cart_preview'] = cart_preview
    return context

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
    # Mostrar vista según tipo de usuario
    if perfil.tipo_cuenta == 'empresa':
        # Dashboard para usuarios empresa
        productos = Producto.objects.filter(usuario=request.user).prefetch_related('imagenes')
        servicios = Servicio.objects.filter(usuario=request.user).prefetch_related('imagenes')
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')[:5]
        context = {
            'perfil': perfil,
            'productos': productos,
            'servicios': servicios,
            'pedidos': pedidos,
            'user': request.user,
        }
        return render(request, 'accounts/home.html', context)
    else:
        # Vista para usuarios consumidores: búsqueda, filtros y categorías
        search_query = request.GET.get('q', '')
        category_filter = request.GET.get('category', '')
        # Query base: productos activos de empresas
        productos_qs = Producto.objects.filter(
            usuario__userprofile__tipo_cuenta='empresa', activo=True
        )
        # Aplicar búsqueda por nombre
        if search_query:
            productos_qs = productos_qs.filter(nombre__icontains=search_query)
        # Aplicar filtro por categoría
        if category_filter:
            productos_qs = productos_qs.filter(categoria=category_filter)
        # Prefetch imágenes
        productos = productos_qs.prefetch_related('imagenes')
        # Listado de categorías para el filtro
        categories = Producto.objects.filter(
            usuario__userprofile__tipo_cuenta='empresa'
        ).values_list('categoria', flat=True).distinct()
        context = {
            'perfil': perfil,
            'productos': productos,
            'user': request.user,
            'search_query': search_query,
            'category_filter': category_filter,
            'categories': categories,
        }
        return render(request, 'accounts/home_consumer.html', context)

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

@login_required(login_url='login')
def cart(request):
    """Muestra el carrito de compras y permite checkout."""
    cart_session = request.session.get('cart', {})
    productos_carrito = []
    total = Decimal('0')
    for prod_id, qty in cart_session.items():
        producto = get_object_or_404(Producto, pk=int(prod_id))
        subtotal = producto.precio * qty
        total += subtotal
        productos_carrito.append({
            'producto': producto,
            'cantidad': qty,
            'subtotal': subtotal,
        })
    # Checkout
    if request.method == 'POST':
        # Procesar compra (simulado)
        request.session['cart'] = {}
        messages.success(request, '¡Compra realizada con éxito!')
        return redirect('home')
    return render(request, 'accounts/cart.html', {
        'productos_carrito': productos_carrito,
        'total': total,
    })

@login_required(login_url='login')
def add_to_cart(request, product_id):
    """Agrega un producto al carrito en sesión."""
    cart_session = request.session.get('cart', {})
    cart_session[str(product_id)] = cart_session.get(str(product_id), 0) + 1
    request.session['cart'] = cart_session
    messages.success(request, 'Producto agregado al carrito.')
    return redirect('home')

@login_required(login_url='login')
def remove_from_cart(request, product_id):
    """Elimina un producto del carrito."""
    cart_session = request.session.get('cart', {})
    if str(product_id) in cart_session:
        del cart_session[str(product_id)]
        request.session['cart'] = cart_session
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cart')

@login_required(login_url='login')
def buy_now(request, product_id):
    """Agrega el producto y redirige al carrito para proceder al pago."""
    cart_session = request.session.get('cart', {})
    cart_session[str(product_id)] = cart_session.get(str(product_id), 0) + 1
    request.session['cart'] = cart_session
    return redirect('cart')

# Vista para crear o editar la landing page de empresas
@login_required(login_url='login')
def create_landing_page(request):
    # Solo empresas pueden acceder
    perfil = get_object_or_404(PerfilUsuario, usuario=request.user)
    if perfil.tipo_cuenta != 'empresa':
        messages.error(request, 'No tienes permiso para crear o editar la página de empresa.')
        return redirect('home')

    # Obtener landing existente o None
    landing = LandingPage.objects.filter(usuario=request.user).first()

    # Obtener algunos productos y servicios para bloques predefinidos
    # NOTA: los [:5] aquí limitan a 5 para el preview, pero más abajo los puedes usar completos
    products = Producto.objects.filter(usuario=request.user, activo=True)[:5]
    services = Servicio.objects.filter(usuario=request.user, activo=True)[:5]

    # ----- AÑADE ESTO: lista de categorías únicas para el slider (hasta 6) -----
    all_cats = (
        Producto.objects
        .filter(usuario=request.user, activo=True)
        .values_list('categoria', flat=True)
        .distinct()[:6]
    )
    categories = list(all_cats)
    # ---------------------------------------------------------------------------

    if request.method == 'POST':
        form = LandingPageForm(request.POST, instance=landing)
        if form.is_valid():
            new_lp = form.save(commit=False)
            new_lp.usuario = request.user
            new_lp.save()
            messages.success(request, '¡Tu página ha sido guardada exitosamente!')
            return redirect('home')
    else:
        form = LandingPageForm(instance=landing)

    return render(request, 'accounts/landingpage_form.html', {
        'form': form,
        'landing': landing,
        'products': products,
        'services': services,
        'categories': categories,   # <--- pásalo al template
    })

# Vista para mostrar la landing page en modo presentación completa
@login_required(login_url='login')
def landingpage_view(request):
    perfil = get_object_or_404(PerfilUsuario, usuario=request.user)
    # Sólo empresas tienen landing page
    if perfil.tipo_cuenta != 'empresa':
        raise Http404('No tienes una página disponible')
    # Obtener landing page
    landing = LandingPage.objects.filter(usuario=request.user).first()
    if not landing:
        raise Http404('Página no encontrada')
    # Datos de productos y servicios si la plantilla los necesita
    products = Producto.objects.filter(usuario=request.user, activo=True)
    services = Servicio.objects.filter(usuario=request.user, activo=True)
    return render(request, 'accounts/landingpage_view.html', {
        'landing': landing,
        'products': products,
        'services': services,
    })

# Vista de marketplace público para consumidores
def marketplace(request):
    # Solo consumidores pueden acceder
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'userprofile', None)
        if perfil and perfil.tipo_cuenta == 'empresa':
            return redirect('home')
    # Listar todas las empresas registradas
    empresas = PerfilUsuario.objects.filter(tipo_cuenta='empresa').select_related('usuario')
    return render(request, 'accounts/marketplace.html', {'empresas': empresas})

# Vista pública de empresa: landing o catálogo
def public_company_page(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    perfil = get_object_or_404(PerfilUsuario, usuario=user_obj)
    if perfil.tipo_cuenta != 'empresa':
        raise Http404('Empresa no encontrada')
    landing = LandingPage.objects.filter(usuario=user_obj).first()
    products = Producto.objects.filter(usuario=user_obj, activo=True).prefetch_related('imagenes')
    services = Servicio.objects.filter(usuario=user_obj, activo=True).prefetch_related('imagenes')
    if landing:
        return render(request, 'accounts/landingpage_view.html', {
            'landing': landing,
            'products': products,
            'services': services,
        })
    # Si no hay landing, mostrar catálogo de productos y servicios
    return render(request, 'accounts/company_catalog.html', {
        'perfil': perfil,
        'products': products,
        'services': services,
    })

# Vista de catálogo completo de empresa (plantilla premium)
def company_full_catalog(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    perfil = get_object_or_404(PerfilUsuario, usuario=user_obj)
    if perfil.tipo_cuenta != 'empresa':
        raise Http404('Empresa no encontrada')
    products = Producto.objects.filter(usuario=user_obj, activo=True).prefetch_related('imagenes')
    services = Servicio.objects.filter(usuario=user_obj, activo=True).prefetch_related('imagenes')
    return render(request, 'accounts/company_full_catalog.html', {
        'perfil': perfil,
        'products': products,
        'services': services,
    })
