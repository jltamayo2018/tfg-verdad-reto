from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
import secrets, string
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils import timezone


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

# Modelo para representar colaboradores de un Pack    
class PackCollaborator(models.Model):
    class Role(models.TextChoices):
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Lector"

    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_packs')
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.EDITOR)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    created_at = models.DateTimeField(auto_now_add=True)

    ROLE_CHOICES = Role.choices
    EDITOR = Role.EDITOR
    VIEWER = Role.VIEWER 

    class Meta:
        unique_together = ('pack', 'user')
        indexes = [
            models.Index(fields=['pack', 'user']),
        ]
        verbose_name = "Colaborador de Pack"
        verbose_name_plural = "Colaboradores de Packs"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) en {self.pack.name}"
    
User = get_user_model()

class VideoRoom(models.Model):
    code = models.SlugField(unique=True, max_length=64, db_index=True)
    pack = models.ForeignKey("verdadoreto_app.Pack", on_delete=models.CASCADE, related_name="video_rooms")
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hosted_video_rooms")
    status = models.CharField(
        max_length=20,
        choices=[("lobby","Lobby"), ("live","En juego"), ("ended","Finalizada")],
        default="lobby",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.CharField(max_length=20, default="jitsi")
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def start_ttl(self, minutes=30):
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save(update_fields=["expires_at"])

    def extend_ttl(self, minutes=30):
        """Renueva la caducidad cuando hay actividad."""
        if not self.expires_at or self.expires_at < timezone.now():
            self.start_ttl(minutes)
        else:
            self.expires_at = timezone.now() + timedelta(minutes=minutes)
            self.save(update_fields=["expires_at"])

    @property
    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()

    @staticmethod
    def generate_code():
        return "vr-" + get_random_string(8) + "-" + get_random_string(8)

    def __str__(self):
        return f"{self.code} — {self.pack} — {self.get_status_display()}"
    
    @classmethod
    def cleanup_expired(cls):
        """Borra todas las salas expiradas. Devuelve cuántas se han borrado."""
        qs = cls.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=timezone.now()
        )
        count = qs.count()
        qs.delete()
        return count

class RoomParticipant(models.Model):
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="video_participations")
    display_name = models.CharField(max_length=60)
    role = models.CharField(max_length=10, choices=[("host","Host"),("player","Player")], default="player")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("room", "user")]  # evita duplicar al mismo user en la sala
        indexes = [models.Index(fields=["room", "role"])]

    def __str__(self):
        return f"{self.display_name} @ {self.room.code} ({self.role})"

class GameState(models.Model):
    room = models.OneToOneField(VideoRoom, on_delete=models.CASCADE, related_name="state")
    current_index = models.IntegerField(default=0)
    seed = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f"State({self.room.code}) idx={self.current_index}"