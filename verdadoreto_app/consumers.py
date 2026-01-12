import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from .models import VideoRoom, GameState, RoomParticipant

logger = logging.getLogger(__name__)


class RoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        self.group = f"room_{self.code}"

        user = self.scope.get("user", AnonymousUser())
        if not user or user.is_anonymous:
            await self.close(code=4401)  # unauthorized
            return

        # Verifica que la sala exista
        exists = await self.room_exists()
        if not exists:
            await self.close(code=4404)  # not found
            return

        # Registrar participante (siempre)
        await self.ensure_participant(user.id)

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Renovamos TTL al conectar
        await self.extend_room_ttl(30)

        # Enviamos el estado actual al cliente
        state = await self.get_state()
        await self.send_json({"event": "state_init", **state})

        # Avisar a todos (por si se quiere mostrar participantes, etc.)
        # await self.channel_layer.group_send(self.group, {"type": "lobby_update"})

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group, self.channel_name)
        except Exception:
            pass
            # logger.exception("Error al descartar canal del grupo en disconnect")

        user = self.scope.get("user", AnonymousUser())
        if user and not user.is_anonymous:
            # Eliminar participante al salir (clave para la lógica de borrado)
            await self.remove_participant(user.id)

        # Renovar TTL un poco y quizá borrar si queda vacía
        await self.extend_room_ttl(10)
        await self.maybe_delete_if_empty()
        
        # Avisar a todos
        try:
            await self.channel_layer.group_send(self.group, {"type": "lobby_update"})
        except Exception:
            pass

        # NO se borra la sala aquí
        # El borrado se hace SOLO por TTL (cleanup_expired)

    async def receive_json(self, content):
        action = content.get("action")
        user = self.scope.get("user", AnonymousUser())

        if not user or user.is_anonymous:
            return

        if action == "join":
            await self.ensure_participant(user.id)
            await self.extend_room_ttl(30)
            await self.channel_layer.group_send(self.group, {"type": "lobby_update"})
            return

        elif action == "start":
            # Solo el host puede iniciar
            if await self.is_host(user.id):
                await self.set_status("live")
                await self.set_index(0)
                await self.extend_room_ttl(30)
                await self.channel_layer.group_send(
                    self.group,
                    {
                        "type": "game_update",
                        "event": "new_question",
                        "index": 0,
                    }
                )
            return

        elif action == "next":
            if await self.is_host(self.scope["user"].id):
                try:
                    idx = max(0, int(content.get("index", 0)))
                except (TypeError, ValueError):
                    return

                await self.set_index(idx)
                await self.extend_room_ttl(30)
                await self.channel_layer.group_send(
                    self.group,
                    {
                        "type": "game_update",
                        "event": "new_question",
                        "index": idx,
                    }
                )
            return

    # =====================
    # WS handlers
    # =====================

    async def game_update(self, event):
        event = dict(event)
        event.pop("type", None)
        await self.send_json(event)

    async def lobby_update(self, event):
        await self.send_json({"event": "lobby_update"})

    # =====================
    # Helpers DB
    # =====================

    @database_sync_to_async
    def room_exists(self) -> bool:
        return VideoRoom.objects.filter(code=self.code).exists()

    @database_sync_to_async
    def get_state(self):
        try:
            room = VideoRoom.objects.get(code=self.code)
        except ObjectDoesNotExist:
            return {"status": "ended", "index": 0}

        st, _ = GameState.objects.get_or_create(room=room)
        return {"status": room.status, "index": st.current_index}

    @database_sync_to_async
    def is_host(self, user_id):
        room = VideoRoom.objects.only("host_id").get(code=self.code)
        return room.host_id == user_id

    @database_sync_to_async
    def set_status(self, status: str):
        VideoRoom.objects.filter(code=self.code).update(status=status)

    @database_sync_to_async
    def set_index(self, idx: int):
        room = VideoRoom.objects.get(code=self.code)
        GameState.objects.update_or_create(room=room, defaults={"current_index": idx})

    @database_sync_to_async
    def extend_room_ttl(self, minutes: int):
        try:
            room = VideoRoom.objects.get(code=self.code)
            room.extend_ttl(minutes)
        except VideoRoom.DoesNotExist:
            pass

    @database_sync_to_async
    def ensure_participant(self, user_id: int):
        room = VideoRoom.objects.get(code=self.code)
        role = "host" if room.host_id == user_id else "player"

        RoomParticipant.objects.update_or_create(
            room=room,
            user_id=user_id,
            defaults={"display_name": room.host.username if role == "host" else room.host.username, "role": role},
        )

    @database_sync_to_async
    def remove_participant(self, user_id: int):
        try:
            room = VideoRoom.objects.get(code=self.code)
        except VideoRoom.DoesNotExist:
            return
        RoomParticipant.objects.filter(room=room, user_id=user_id).delete()

    @database_sync_to_async
    def maybe_delete_if_empty(self):
        try:
            room = VideoRoom.objects.get(code=self.code)
        except VideoRoom.DoesNotExist:
            return

        # Solo borramos si sigue en lobby y no queda nadie
        if room.status == "lobby":
            if not RoomParticipant.objects.filter(room=room).exists():
                room.delete()