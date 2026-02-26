import random
from django.utils.deprecation import MiddlewareMixin
from .models import VideoRoom

class CleanupVideoRoomsMiddleware(MiddlewareMixin):
    # Limpia salas expiradas automáticamente.
    # Para no cargar demasiado la BD, solo se ejecuta en un % de las peticiones.

    def process_request(self, request):
        # 20% de las peticiones disparan limpieza (ajusta entre 0 y 1 si quieres)
        if random.random() < 0.2:
            VideoRoom.cleanup_expired()
        # Siempre devolvemos None para que siga el flujo normal
        return None
