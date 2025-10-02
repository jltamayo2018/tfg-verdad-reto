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
]

@receiver(post_save, sender=User)
def crear_packs_predeterminados(sender, instance: AbstractBaseUser, created: bool, **kwargs):
    if not created:
        return
    if Pack.objects.filter(owner=instance).exists():
        return

    with transaction.atomic():
        for pack_def in DEFAULT_PACKS:
            pack = Pack.objects.create(owner=instance, name=pack_def["name"])
            acciones = [
                Action(pack=pack, type=acc["type"], text=acc["text"], active=True)
                for acc in pack_def["acciones"]
            ]
            Action.objects.bulk_create(acciones)
