# verdadoreto_app/signals.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Pack, Action

User = get_user_model()

DEFAULT_PACKS = [
    {
        "name": "Fiesta",
        "category": Pack.Category.FIESTA,
        "level": 2,
        "acciones": [
            {"type": Action.Type.VERDAD, "text": "¿Cuál ha sido tu mayor metedura de pata en una fiesta?"},
            {"type": Action.Type.VERDAD, "text": "¿Has mentido hoy a alguien del grupo?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué es lo más loco que has hecho de viaje?"},
            {"type": Action.Type.VERDAD, "text": "Confiesa un crush inesperado."},
            {"type": Action.Type.VERDAD, "text": "¿Qué hábito vergonzoso tienes en secreto?"},
            {"type": Action.Type.VERDAD, "text": "¿Cuál fue tu primer beso y cómo fue?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué es lo último que buscaste en tu móvil?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué te da más cringe de ti?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué rumor te gustaría desmentir de ti?"},
            {"type": Action.Type.VERDAD, "text": "Cuenta una verdad incómoda de tu infancia."},

            {"type": Action.Type.RETO, "text": "Baila 30 segundos al ritmo que te pongan."},
            {"type": Action.Type.RETO, "text": "Envía un sticker random al último chat de WhatsApp."},
            {"type": Action.Type.RETO, "text": "Haz una imitación de alguien del grupo."},
            {"type": Action.Type.RETO, "text": "Habla con voz de locutor por 1 minuto."},
            {"type": Action.Type.RETO, "text": "Selfie grupal con tu peor cara."},
            {"type": Action.Type.RETO, "text": "Intercambia el móvil con alguien durante 1 minuto."},
            {"type": Action.Type.RETO, "text": "Cuenta un chiste. Si nadie se ríe, canta."},
            {"type": Action.Type.RETO, "text": "Habla sin vocales por 30 segundos."},
            {"type": Action.Type.RETO, "text": "Pon un estado en IG solo con emojis por 5 min."},
            {"type": Action.Type.RETO, "text": "Deja que alguien te cambie el peinado."},
        ]
    },
    {
        "name": "Picante",
        "category": Pack.Category.PICANTE,
        "level": 4,
        "acciones": [
            {"type": Action.Type.VERDAD, "text": "¿Cuál es tu mayor fetiche (si te atreves a decirlo)?"},
            {"type": Action.Type.VERDAD, "text": "¿Has tenido un sueño subido de tono con alguien del grupo?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué es lo más atrevido que has enviado por chat?"},
            {"type": Action.Type.VERDAD, "text": "¿Con quién tendrías una cita a ciegas ahora mismo?"},
            {"type": Action.Type.VERDAD, "text": "Di algo que te encienda y algo que te apague al instante."},

            {"type": Action.Type.RETO, "text": "Envía un 😏 a tu último chat con el texto: “Luego te cuento…”"},
            {"type": Action.Type.RETO, "text": "Lee en voz alta el último mensaje que te hayan enviado con voz seductora."},
            {"type": Action.Type.RETO, "text": "Haz un piropo elegante a la persona de tu izquierda."},
            {"type": Action.Type.RETO, "text": "Baila pegado/a 20 segundos con quien el grupo elija (con consentimiento)."},
            {"type": Action.Type.RETO, "text": "Di tu top 3 de celebrities con las que tendrías una cita."},
        ],
    },
    {
        "name": "Familiar",
        "category": Pack.Category.FAMILIAR,
        "level": 1,
        "acciones": [
            {"type": Action.Type.VERDAD, "text": "Cuenta una anécdota divertida de cuando eras peque."},
            {"type": Action.Type.VERDAD, "text": "¿Cuál es tu comida casera favorita y por qué?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué tradición familiar te encanta mantener?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué es lo más travieso que hiciste en el cole?"},
            {"type": Action.Type.VERDAD, "text": "Nombra a un familiar que te inspire y por qué."},

            {"type": Action.Type.RETO, "text": "Imita a un miembro de tu familia (con cariño)."},
            {"type": Action.Type.RETO, "text": "Cuéntanos un chiste apto para toda la familia."},
            {"type": Action.Type.RETO, "text": "Haz una ‘coreo’ de 10 seg con otra persona del grupo."},
            {"type": Action.Type.RETO, "text": "Di 3 cosas por las que estés agradecido/a hoy."},
            {"type": Action.Type.RETO, "text": "Cuenta una curiosidad tuya que casi nadie conozca."},
        ],
    },
    {
        "name": "En pareja",
        "category": Pack.Category.ROMANTICO,
        "level": 3,
        "acciones": [
            {"type": Action.Type.VERDAD, "text": "Describe tu cita ideal en una frase."},
            {"type": Action.Type.VERDAD, "text": "¿Qué detalle romántico te marcó alguna vez?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué canción asocias con el amor?"},
            {"type": Action.Type.VERDAD, "text": "¿Qué valoras más en una relación?"},
            {"type": Action.Type.VERDAD, "text": "Confiesa un gesto cursi que te encanta (aunque no lo admitas)."},            

            {"type": Action.Type.RETO, "text": "Di un cumplido sincero a la persona que el grupo elija."},
            {"type": Action.Type.RETO, "text": "Escribe un mini poema de 2 líneas y léelo en voz alta."},
            {"type": Action.Type.RETO, "text": "Haz un ‘corazón’ con las manos y dedícalo a alguien del grupo."},
            {"type": Action.Type.RETO, "text": "Recuerda en voz alta tu escena romántica favorita de una peli/serie."},
            {"type": Action.Type.RETO, "text": "Cuenta tu plan perfecto de domingo en pareja."},
        ],
    },
]

@receiver(post_save, sender=User)
def crear_packs_predeterminados(sender, instance: AbstractBaseUser, created: bool, **kwargs):
    if not created:
        return
    if Pack.objects.filter(owner=instance).exists():
        return

    with transaction.atomic():
        for pack_def in DEFAULT_PACKS:
            pack = Pack.objects.create(
                owner=instance, 
                name=pack_def["name"],
                category=pack_def.get("category", Pack.Category.RANDOM),
                level=pack_def.get("level", 3),
            )
            acciones = [
                Action(pack=pack, type=acc["type"], text=acc["text"], active=True)
                for acc in pack_def["acciones"]
            ]
            Action.objects.bulk_create(acciones)
