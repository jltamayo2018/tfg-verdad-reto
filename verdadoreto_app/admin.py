from django.contrib import admin
from .models import Pack, Action, VideoRoom, RoomParticipant, GameState

# Este fichero sirve para registrar tus modelos en el panel de administración de Django

@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'creation_date')
    search_fields = ('name', 'owner__username')
    list_filter = ('creation_date', 'owner')
    # readonly_fields = ('token')

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('get_type_display', 'text_short', 'pack', 'active', 'created_at')
    list_filter = ('type', 'active', 'created_at', 'pack')
    search_fields = ('text', 'pack__name')

    def text_short(self, obj):
        return (obj.text[:60] + '…') if len(obj.text) > 60 else obj.text
    text_short.short_description = 'Texto'

@admin.register(VideoRoom)
class VideoRoomAdmin(admin.ModelAdmin):
    list_display = ("code", "pack", "host", "status", "created_at")
    search_fields = ("code",)
    list_filter = ("status",)

@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ("room", "display_name", "role", "joined_at")
    list_filter = ("role",)

@admin.register(GameState)
class GameStateAdmin(admin.ModelAdmin):
    list_display = ("room", "current_index")