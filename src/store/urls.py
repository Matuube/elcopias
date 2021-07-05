from django.conf.urls import url
from django.urls import path
from store import views
from django.contrib.auth import views as auth_views


app_name = 'store'

urlpatterns = [
    # Indice
    path("index/", views.index, name = "index"),
    path("acerca_de/", views.acerca_de, name="acerca_de"),
    
    # Registro
    path("registro/", views.sign_up_form, name = "registro"),
    path("registro/resultado_registro/", views.resultado_registro, name = "resultado_registro"),
    
    # Login
    path("login/", views.login_form, name = "login"),
    path("login/resultado_login/", views.resultado_login, name = "resultado_login"),
    path("logout/", views.sign_out, name = "logout"),
   
    # Producto
    path('producto/<int:pk>/', views.VistaProducto.as_view(), name='producto'),
    
    # Carrito
    path('agregar_al_carrito/<pk>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('quitar_del_carrito/<pk>/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('reducir_cantidad_producto/<pk>/', views.reducir_cantidad_producto, name='reducir_cantidad_producto'),
    path('resumen_compra/', views.VistaResumenCompra.as_view(), name='resumen_compra'),
    path('eliminar_carrito/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito_eliminado/', views.carrito_eliminado, name='carrito_eliminado'),
    
    # Búsqueda
    path('resultado_busqueda/', views.ResultadoBusqueda.as_view(), name='resultado_busqueda'),
    path('resultado_busqueda_categoria/', views.ResultadoBusquedaCategoria.as_view(), name='resultado_busqueda_categoria'),

    # Nuevo producto
    path('nuevo_producto/', views.NuevoProductoView.as_view(), name= 'nuevo_producto'),
    path('nuevo_producto/nuevo_producto_resultado', views.nuevo_producto_resultado, name= 'nuevo_producto_resultado'),

    # Actualizar producto
    path('actualizar_producto/<int:pk>', views.EditarProductoView.as_view(), name= 'actualizar_producto'),
    path('actualizar_producto/producto_actualizado', views.producto_actualizado, name= 'producto_actualizado'),

    # Eliminar producto
    path('eliminar_producto/<int:pk>', views.EliminarProductoView.as_view(), name= 'eliminar_producto'),
    path('eliminar_producto/producto_eliminado', views.producto_eliminado, name= 'producto_eliminado'),

    
]