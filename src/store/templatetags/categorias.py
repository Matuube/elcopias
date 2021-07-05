from store.models import Categoria
from django import template

register = template.Library()

@register.inclusion_tag('categorias.html')
def mostrar_categorias():
    return {'categorias': Categoria.objects.all()}