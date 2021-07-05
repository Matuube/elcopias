from django import template
from django.db.models.query import EmptyQuerySet
from django.shortcuts import render
from django.http import HttpResponse # This takes http requests
from . import forms
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.utils import timezone
from .models import Categoria, Producto, Carrito, ProductoAgregado
from store.forms import NuevoProductoForm
from django.db.models import Q, F
import pprint
import json
import random


# Create your views here.
def index(request):
    productos = Producto.objects.all()
    productos_ordenados = productos.order_by('-fecha_creacion')

    index = 0
    tres_productos = []
    while index < 3:
        un_producto = productos_ordenados[index]
        tres_productos.append(un_producto)
        index +=1

    index = 3
    siete_productos = []
    while index < 10:
        un_producto = productos_ordenados[index]
        siete_productos.append(un_producto)
        index +=1

    print(productos)
    dictionary = {
        'tres_productos': tres_productos,
        'siete_productos': siete_productos,
    }
    return render(request, 'index.html', context=dictionary)

def acerca_de(request):
    dictionary={}
    return render(request, 'acerca_de.html', context=dictionary)

def sign_up_form(request):
    form = forms.SignUpForm() # class defined in forms.py
    dictionary = {"form": form}
    
    if request.method == "POST":
        form = forms.SignUpForm(request.POST) # creating a variable that receives the POST
        if form.is_valid(): 
            password = form.clean_password2()
            user = form.save(commit=False)
            user.save()
            grupo_estandar = Group.objects.get(name='Estandar')
            user.groups.add(grupo_estandar)
            
            form.save()

            return redirect('resultado_registro/')
        else:
            print("Invalid form request")
            error = form.errors
            print(error)
            dictionary = {
                'error': error
            }    
    else:
        form = forms.SignUpForm()
    
    dictionary = {
            'form': form
            }    
    return render(request, "registro.html", context=dictionary)

def resultado_registro(request):
    dictionary = {}
    return render(request, "resultado_registro.html", context=dictionary)

def login_form(request):
    username = 'not logged in'
    user = request.user
    form = AuthenticationForm()
    dictionary = {
        'form': form
    }
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username and password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        request.session['username'] = username
                        login(request, user)
            print('form and session started')
            return redirect('resultado_login/')
        else:
            error = form.errors
            print(error)
            dictionary = {
                'error': error
            }
    else:
        form = AuthenticationForm()

    dictionary = {
    'object_list': user,
    'form': form,
    }
          
    return render(request, "login.html", context=dictionary)

def resultado_login(request):
    dictionary = {}
    return render(request, "resultado_login.html", context=dictionary)

@login_required(login_url='/login/')
def sign_out(request): # my logout view
    request.session.clear()
    logout(request)
    print("All sessions closed")
    return render(request, "logout.html")

class VistaProducto(DetailView):
    model = Producto
    template_name = "producto.html"

class VistaResumenCompra(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    def get(self, *args, **kwargs):
        try:
            compra = Carrito.objects.get(usuario=self.request.user, ya_pedido=False)
            contexto= {
                'objeto': compra
            }
            return render(self.request, 'resumen_compra.html', context=contexto)
        except ObjectDoesNotExist:
            messages.error(self.request, 'No tiene un carrito todavía')
            return redirect('/')

@login_required(login_url= '/login/')
def agregar_al_carrito(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto_agregado, creado = ProductoAgregado.objects.get_or_create(
        producto = producto,
        usuario = request.user,
        ya_agregado = False
    )

    producto_existente_carrito = Carrito.objects.filter(usuario=request.user, ya_pedido=False)

    if producto_existente_carrito.exists():
        agrega_producto = producto_existente_carrito[0]

        if agrega_producto.productos.filter(producto__pk=producto.pk).exists():
            producto_agregado.cantidad += 1
            producto_agregado.save()
            messages.info(request, "Agregada/s unidad/es")
            return redirect("store:resumen_compra")
        else:
            agrega_producto.productos.add(producto_agregado)
            messages.info(request, 'Producto agregado al carrito')
            return redirect("store:resumen_compra")
    else:
        fecha_pedido = timezone.now()
        agregado_al_pedido = Carrito.objects.create(usuario=request.user, fecha=fecha_pedido)
        agregado_al_pedido.productos.add(producto_agregado)
        messages.info(request, "Producto agregado al carrito")
        return redirect('store:resumen_compra')


@login_required
def quitar_del_carrito(request, pk):
    producto = get_object_or_404(Producto, pk=pk )
    producto_existente = Carrito.objects.filter(usuario=request.user, ya_pedido=False)

    if producto_existente.exists():
        quita_producto = producto_existente[0]
        if quita_producto.productos.filter(producto__pk=producto.pk).exists():
            producto_en_lista = ProductoAgregado.objects.filter(   producto=producto,
                usuario=request.user,
                ya_agregado=False
            )[0]
            producto_en_lista.delete()
            messages.info(request, "Item \""+producto_en_lista.producto.titulo+"\" retirado del carrito")
            return redirect("store:resumen_compra")
        else:
            messages.info(request, "Este producto no está en su carrito")
            return redirect("store:producto", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "No tiene un carrito")
        return redirect("store:producto", pk = pk)

@login_required
def eliminar_carrito(request):
    productos_del_usuario = Carrito.objects.filter(usuario=request.user, ya_pedido=False)

    if productos_del_usuario.exists():
        Carrito.objects.filter(usuario=request.user, ya_pedido=False).delete()
        ProductoAgregado.objects.filter(usuario=request.user, ya_agregado=False).delete()
        Carrito.objects.create(usuario=request.user)

        return redirect("store:carrito_eliminado")
    else:
        #add message doesnt have order
        messages.info(request, "No tiene un carrito")
        return redirect("/")

def carrito_eliminado(request):
    dictionary = {}
    return render(request, "carrito_eliminado.html", context=dictionary)

@login_required
def reducir_cantidad_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk )
    producto_existente = Carrito.objects.filter(
        usuario = request.user, 
        ya_pedido = False
    )
    if producto_existente.exists():
        quita_producto = producto_existente[0]
        if quita_producto.productos.filter(producto__pk=producto.pk).exists() :
            item = ProductoAgregado.objects.filter(
                producto = producto,
                usuario = request.user,
                ya_agregado = False
            )[0]
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
            messages.info(request, "La cantidad fue modificada")
            return redirect("store:resumen_compra")
        else:
            messages.info(request, "Este item no esta en su lista")
            return redirect("store:resumen_compra")
    else:
        #add message doesnt have order
        messages.info(request, "No tiene un carrito")
        return redirect("store:resumen_compra")

class NuevoProductoView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    permission_required = 'store.can_add_productos'
    
    form_class = NuevoProductoForm
    template_name = 'nuevo_producto.html'
    success_url = 'nuevo_producto_resultado'

def nuevo_producto_resultado(request):
    dictionary = {}
    return render(request, "nuevo_producto_resultado.html", context=dictionary)

class ResultadoBusqueda(ListView):
    model = Producto
    template_name = 'resultado_busqueda.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            queryset = Producto.objects.filter(
                Q(titulo__icontains=query) | Q(categoria_base__descripcion__icontains=query) | Q(detalle__icontains=query)
        )
            print(queryset)
        else:
            queryset = Producto.objects.all()

        return queryset


class ResultadoBusquedaCategoria(ListView):
    model = Producto
    template_name = 'resultado_busqueda_categoria.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        print(query)
        if query:
            queryset = Producto.objects.filter(Q(categoria_base__descripcion__icontains=query))
            print(queryset)
        else:
            queryset = Producto.objects.all()

        return queryset

class EditarProductoView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    permission_required = 'store.can_add_productos'
    
    model = Producto
    template_name = 'actualizar_producto.html'
    success_url = 'producto_actualizado'
    fields=[
            'titulo','categoria_base','detalle','precio','imagen'
        ]

def producto_actualizado(request):
    dictionary = {}
    return render(request, "producto_actualizado.html", context=dictionary)


class EliminarProductoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    permission_required = 'store.can_add_productos'
    
    model = Producto
    template_name = 'eliminar_producto.html'
    success_url = 'producto_eliminado'
    fields=[
            'titulo','categoria_base','detalle','precio','imagen'
        ]

def producto_eliminado(request):
    dictionary = {}
    return render(request, "producto_eliminado.html", context=dictionary)