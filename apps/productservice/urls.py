from django.urls import path
from apps.productservice import views

urlpatterns = [
    path('productos/', views.productos, name='productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/imagen/eliminar/<int:imagen_id>/', views.eliminar_imagen_producto, name='eliminar_imagen_producto'),
    path('productos/imagen/principal/<int:imagen_id>/', views.marcar_principal_imagen_producto, name='marcar_principal_imagen_producto'),
    path('servicios/', views.servicios, name='servicios'),
    path('servicios/crear/', views.crear_servicio, name='crear_servicio'),
    path('servicios/editar/<int:pk>/', views.editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:pk>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('servicios/imagen/eliminar/<int:imagen_id>/', views.eliminar_imagen_servicio, name='eliminar_imagen_servicio'),
    path('servicios/imagen/principal/<int:imagen_id>/', views.marcar_principal_imagen_servicio, name='marcar_principal_imagen_servicio'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('servicio/<int:pk>/', views.detalle_servicio, name='detalle_servicio'),
] 