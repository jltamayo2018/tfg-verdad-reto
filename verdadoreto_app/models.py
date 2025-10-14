from django.db import models
from django.contrib.auth.models import User
import secrets, string
from django.core.validators import MinValueValidator, MaxValueValidator

# función para generar un token aleatorio para los enlaces de los packs
def generar_token(length=22):
    alfabeto = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alfabeto) for _ in range(length))

# Modelo para representar un Pack asociado a un usuario
class Pack(models.Model):
    class Category(models.TextChoices):
        PICANTE = "🔥 PICANTE", "🔥 Picante"
        FIESTA = "🎉 FIESTA", "🎉 Fiesta"
        FAMILIAR = "👪 FAMILIAR", "👪 Familiar"
        ROMANTICO = "❤️ ROMÁNTICO", "❤️ Romántico"
        RANDOM = "🎲 RANDOM", "🎲 Random"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='packs')
    name = models.CharField(max_length=120)
    creation_date = models.DateTimeField(auto_now_add=True)

    # Único identificador público
    token = models.CharField(max_length=32, unique=True, editable=False, db_index=True)
    
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.RANDOM)
    level = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def save(self, *args, **kwargs):
        # Genera el token principal solo si no existe aún
        if not self.token:
            self.token = generar_token()
        super().save(*args, **kwargs)

    @staticmethod
    def _token_unico():
        # Reintenta hasta asegurar unicidad
        while True:
            t = generar_token()
            if not Pack.objects.filter(
                models.Q(token=t)
            ).exists():
                return t

    def __str__(self):
        return f"{self.name} (de {self.owner.username})"


    def regenerate_unified(self):
        self.token = self._token_unico()
        self.save(update_fields=['token'])

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