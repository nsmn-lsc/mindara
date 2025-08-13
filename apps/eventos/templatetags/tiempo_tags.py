from django import template
from django.utils import timezone
from datetime import datetime
import math

register = template.Library()

@register.filter
def tiempo_elegante(date):
    """
    Convierte una fecha en una representación elegante del tiempo transcurrido
    """
    if not date:
        return "Fecha no disponible"
    
    # Asegurar que date tenga timezone info
    if timezone.is_naive(date):
        date = timezone.make_aware(date)
    
    now = timezone.now()
    diff = now - date
    
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = diff.days % 30
    
    if years > 0:
        if years == 1:
            return f"{years} año"
        else:
            return f"{years} años"
    elif months > 0:
        if months == 1:
            return f"{months} mes"
        else:
            return f"{months} meses"
    elif days > 0:
        if days == 1:
            return f"{days} día"
        else:
            return f"{days} días"
    else:
        hours = diff.seconds // 3600
        if hours > 0:
            if hours == 1:
                return f"{hours} hora"
            else:
                return f"{hours} horas"
        else:
            return "Hoy"

@register.filter
def tiempo_desde(date):
    """
    Versión simplificada que solo muestra la unidad más grande
    """
    if not date:
        return "N/A"
    
    # Asegurar que date tenga timezone info
    if timezone.is_naive(date):
        date = timezone.make_aware(date)
    
    now = timezone.now()
    diff = now - date
    
    years = diff.days // 365
    months = (diff.days % 365) // 30
    
    if years > 0:
        return f"{years} año{'s' if years != 1 else ''}"
    elif months > 0:
        return f"{months} mes{'es' if months != 1 else ''}"
    else:
        days = diff.days
        if days > 0:
            return f"{days} día{'s' if days != 1 else ''}"
        else:
            return "Menos de un día"
