from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from .models import VideoRoom, GameState


class RoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        self.group = f"room_{self.code}"

        user = self.scope.get("user", AnonymousUser())
        if not user or user.is_anonymous:
            await self.close()
            return

        # Verifica que la sala exista
        exists = await self.room_exists()
        if not exists:
            await self.close()
            return

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Renovamos TTL al conectar
        await self._extend_room_ttl(30)

        # Enviamos el estado actual al cliente
        state = await self.get_state()
        await self.send_json({"event": "state_init", **state})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

        # Notificamos cambios de lobby (UI)
        await self.channel_layer.group_send(
            self.group,
            {"type": "lobby_update"}
        )

        # TTL corto para permitir reconexión
        await self._extend_room_ttl(10)

        # ❌ NO se borra la sala aquí
        # El borrado se hace SOLO por TTL (cleanup_expired)

    async def receive_json(self, content):
        action = content.get("action")

        if action == "join":
            await self._extend_room_ttl(30)
            await self.channel_layer.group_send(
                self.group,
                {"type": "lobby_update"}
            )

        elif action == "start":
            # Solo el host puede iniciar
            if await self.is_host(self.scope["user"].id):
                await self.set_status("live")
                await self.set_index(0)
                await self._extend_room_ttl(30)
                await self.channel_layer.group_send(
                    self.group,
                    {
                        "type": "game_update",
                        "event": "new_question",
                        "index": 0,
                    }
                )

        elif action == "next":
            if await self.is_host(self.scope["user"].id):
                try:
                    idx = max(0, int(content.get("index", 0)))
                except (TypeError, ValueError):
                    return

                await self.set_index(idx)
                await self._extend_room_ttl(30)
                await self.channel_layer.group_send(
                    self.group,
                    {
                        "type": "game_update",
                        "event": "new_question",
                        "index": idx,
                    }
                )

    # =====================
    # WS handlers
    # =====================

    async def game_update(self, event):
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
    def set_status(self, status):
        VideoRoom.objects.filter(code=self.code).update(status=status)

    @database_sync_to_async
    def set_index(self, idx):
        room = VideoRoom.objects.get(code=self.code)
        GameState.objects.update_or_create(
            room=room,
            defaults={"current_index": idx},
        )

    @database_sync_to_async
    def _extend_room_ttl(self, minutes: int):
        try:
            room = VideoRoom.objects.get(code=self.code)
            room.extend_ttl(minutes)
        except VideoRoom.DoesNotExist:
            pass
