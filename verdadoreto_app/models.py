from django.db import models
from django.contrib.auth.models import User
import secrets
import string

# función para generar un token aleatorio para los enlaces de los packs
def generar_token(length=22):
    alfabeto = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alfabeto) for _ in range(length))

# Modelo para representar un Pack asociado a un usuario
class Pack(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='packs')
    name = models.CharField(max_length=120)
    creation_date = models.DateTimeField(auto_now_add=True)

    # Dos identificadores públicos, uno por tipo
    token_verdad = models.CharField(max_length=32, unique=True, editable=False, blank=True)
    token_reto   = models.CharField(max_length=32, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        # Genera tokens solo si no existen aún
        if not self.token_verdad:
            self.token_verdad = generar_token()
        if not self.token_reto:
            self.token_reto = generar_token()
        super().save(*args, **kwargs)

    @staticmethod
    def _token_unico():
        # Reintenta hasta asegurar unicidad
        while True:
            t = generar_token()
            if not Pack.objects.filter(models.Q(token_verdad=t) | models.Q(token_reto=t)).exists():
                return t

    def __str__(self):
        return f"{self.name} (de {self.owner.username})"

    def regenerate(self, kind: str):
        kind = kind.lower()
        if kind == 'verdad':
            self.token_verdad = self._token_unico()
            self.save(update_fields=['token_verdad'])
        elif kind == 'reto':
            self.token_reto = self._token_unico()
            self.save(update_fields=['token_reto'])
        else:
            raise ValueError("kind debe ser 'verdad' o 'reto'")

# Modelo para representar una Acción (Verdad o Reto) dentro de un Pack
class Action(models.Model):
    class Type(models.TextChoices):
        VERDAD = 'VERDAD', 'Verdad'
        RETO   = 'RETO',   'Reto'

    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='actions')
    type = models.CharField(max_length=6, choices=Type.choices)
    text = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_type_display()}] {self.text[:40]}..."