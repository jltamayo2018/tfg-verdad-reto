from django import template
register = template.Library()

# Muestra las estrellas de un pack en la página de detalles. Ej. "★★★☆☆".
@register.simple_tag # Registra un template tag personalinzado, se usa en las plantillas
def stars(n, maxn=5):
    try:
        n = int(n)
    except Exception:
        n = 0
    n = max(0, min(n, maxn))
    return "★" * n + "☆" * (maxn - n)

# Muestra las estrellas de un pack en formato compacto, para la pág Mis packs. Ej. "3★".
@register.simple_tag
def stars_compact(n, maxn=5):
    """Versión compacta: muestra '3★' en lugar de las 5 estrellas."""
    try:
        n = int(n)
    except Exception:
        n = 0
    n = max(0, min(n, maxn))
    return f"{n}★"