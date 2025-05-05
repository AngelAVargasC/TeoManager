from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.productservice.models import Producto, Servicio, Pedido, ImagenProducto, ImagenServicio
from apps.productservice.forms import ProductoForm, ServicioForm

# Create your views here.

# Vista que muestra la lista de productos del usuario autenticado.
@login_required(login_url='login')
def productos(request):
    productos = Producto.objects.filter(usuario=request.user).prefetch_related('imagenes')
    return render(request, 'productservice/productos.html', {'productos': productos})

# Vista para crear un nuevo producto. Muestra y procesa el formulario de creación.
@login_required(login_url='login')
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.usuario = request.user
            producto.save()
            for img in request.FILES.getlist('imagen')[:5]:
                ImagenProducto.objects.create(producto=producto, imagen=img)
            messages.success(request, '¡Producto creado correctamente!')
            return redirect('productos')
    else:
        form = ProductoForm()
    return render(request, 'productservice/producto_form.html', {'form': form, 'titulo': 'Crear Producto'})

# Vista para editar un producto existente. Muestra y procesa el formulario de edición.
@login_required(login_url='login')
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, usuario=request.user)
    imagenes_actuales = producto.imagenes.all()
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        nuevas_imagenes = request.FILES.getlist('imagen')
        if form.is_valid():
            form.save()
            if nuevas_imagenes:
                total_imagenes = imagenes_actuales.count() + len(nuevas_imagenes)
                if total_imagenes > 5:
                    messages.error(request, 'Solo puedes tener hasta 5 imágenes por producto.')
                else:
                    for img in nuevas_imagenes:
                        ImagenProducto.objects.create(producto=producto, imagen=img)
                    messages.success(request, '¡Producto actualizado correctamente!')
            else:
                messages.success(request, '¡Producto actualizado correctamente!')
            return redirect('productos')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productservice/producto_form.html', {
        'form': form,
        'titulo': 'Editar Producto',
        'imagenes': imagenes_actuales,
        'producto': producto
    })

# Vista para eliminar un producto existente. Confirma y procesa la eliminación.
@login_required(login_url='login')
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, usuario=request.user)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, '¡Producto eliminado correctamente!')
        return redirect('productos')
    return render(request, 'productservice/producto_confirm_delete.html', {'producto': producto})

# Vista para eliminar una imagen de un producto.
@login_required(login_url='login')
def eliminar_imagen_producto(request, imagen_id):
    imagen = get_object_or_404(ImagenProducto, id=imagen_id, producto__usuario=request.user)
    producto_id = imagen.producto.id
    imagen.delete()
    messages.success(request, '¡Imagen eliminada correctamente!')
    return redirect('editar_producto', pk=producto_id)

# Vista que muestra la lista de servicios del usuario autenticado.
@login_required(login_url='login')
def servicios(request):
    servicios = Servicio.objects.filter(usuario=request.user).prefetch_related('imagenes')
    return render(request, 'productservice/servicios.html', {'servicios': servicios})

# Vista que muestra la lista de pedidos del usuario autenticado.
@login_required(login_url='login')
def pedidos(request):
    return render(request, 'productservice/pedidos.html')

# Vista para crear un nuevo servicio. Muestra y procesa el formulario de creación.
@login_required(login_url='login')
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.usuario = request.user
            servicio.save()
            for img in request.FILES.getlist('imagen')[:5]:
                ImagenServicio.objects.create(servicio=servicio, imagen=img)
            messages.success(request, '¡Servicio creado correctamente!')
            return redirect('servicios')
    else:
        form = ServicioForm()
    return render(request, 'productservice/servicio_form.html', {'form': form, 'titulo': 'Crear Servicio'})

# Vista para editar un servicio existente. Muestra y procesa el formulario de edición.
@login_required(login_url='login')
def editar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk, usuario=request.user)
    imagenes_actuales = servicio.imagenes.all()
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        nuevas_imagenes = request.FILES.getlist('imagen')
        if form.is_valid():
            form.save()
            if nuevas_imagenes:
                total_imagenes = imagenes_actuales.count() + len(nuevas_imagenes)
                if total_imagenes > 5:
                    messages.error(request, 'Solo puedes tener hasta 5 imágenes por servicio.')
                else:
                    for img in nuevas_imagenes:
                        ImagenServicio.objects.create(servicio=servicio, imagen=img)
                    messages.success(request, '¡Servicio actualizado correctamente!')
            else:
                messages.success(request, '¡Servicio actualizado correctamente!')
            return redirect('servicios')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'productservice/servicio_form.html', {
        'form': form,
        'titulo': 'Editar Servicio',
        'imagenes': imagenes_actuales,
        'servicio': servicio
    })

# Vista para eliminar un servicio existente. Confirma y procesa la eliminación.
@login_required(login_url='login')
def eliminar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk, usuario=request.user)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, '¡Servicio eliminado correctamente!')
        return redirect('servicios')
    return render(request, 'productservice/servicio_confirm_delete.html', {'servicio': servicio})

# Vista para eliminar una imagen de un servicio.
@login_required(login_url='login')
def eliminar_imagen_servicio(request, imagen_id):
    imagen = get_object_or_404(ImagenServicio, id=imagen_id, servicio__usuario=request.user)
    servicio_id = imagen.servicio.id
    imagen.delete()
    messages.success(request, '¡Imagen eliminada correctamente!')
    return redirect('editar_servicio', pk=servicio_id)

# Vista para marcar una imagen de producto como principal.
@login_required(login_url='login')
def marcar_principal_imagen_producto(request, imagen_id):
    imagen = get_object_or_404(ImagenProducto, id=imagen_id, producto__usuario=request.user)
    producto = imagen.producto
    if request.method == 'POST':
        producto.imagenes.update(principal=False)
        imagen.principal = True
        imagen.save()
        messages.success(request, '¡Imagen marcada como principal!')
    return redirect('editar_producto', pk=producto.pk)

# Vista para marcar una imagen de servicio como principal.
@login_required(login_url='login')
def marcar_principal_imagen_servicio(request, imagen_id):
    imagen = get_object_or_404(ImagenServicio, id=imagen_id, servicio__usuario=request.user)
    servicio = imagen.servicio
    if request.method == 'POST':
        servicio.imagenes.update(principal=False)
        imagen.principal = True
        imagen.save()
        messages.success(request, '¡Imagen marcada como principal!')
    return redirect('editar_servicio', pk=servicio.pk)
