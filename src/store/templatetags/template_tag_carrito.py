from django import template
from store.models import Carrito

register = template.Library()

@register.filter
def contar_productos(usuario):
    if usuario.is_authenticated:
        qs = Carrito.objects.filter(usuario=usuario, ya_pedido=False)
        if qs.exists():
            return qs[0].productos.count()
    return 0