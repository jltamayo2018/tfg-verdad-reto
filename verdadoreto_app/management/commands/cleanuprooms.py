from django.core.management.base import BaseCommand
from django.utils import timezone
from verdadoreto_app.models import VideoRoom

class Command(BaseCommand):
    help = "Elimina salas expiradas junto con sus estados y participantes."

    def handle(self, *args, **options):
        now = timezone.now()
        expired_rooms = VideoRoom.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=now
        )

        count = expired_rooms.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No expired rooms to delete."))
            return

        expired_rooms.delete()  # se eliminan también GameState y RoomParticipant por cascade
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} expired rooms."))
