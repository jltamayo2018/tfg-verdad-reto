from django import template
register = template.Library()

@register.simple_tag
def stars(n, maxn=5):
    try:
        n = int(n)
    except Exception:
        n = 0
    n = max(0, min(n, maxn))
    return "★" * n + "☆" * (maxn - n)
