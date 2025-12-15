from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),

    # áreas privadas (requieren login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('packs/new/', views.pack_create, name='pack_create'),
    path('packs/<int:pk>/', views.pack_detail, name='pack_detail'),
    path('packs/<int:pk>/qr.png', views.qr_image, name='qr_image'),
    path('packs/<int:pk>/links/regenerate/', views.link_regenerate, name='link_regenerate'),

    # gestión de packs
    path('packs/<int:pk>/collaborators/add/', views.add_collaborator, name='add_collaborator'),
    path('packs/<int:pk>/collaborators/<int:user_id>/remove/', views.remove_collaborator, name='remove_collaborator'),
    path('packs-compartidos/', views.shared_packs, name='shared_packs'),
    
    # acciones dentro de un pack
    path('packs/<int:pk>/actions/new/<str:tipo>/', views.action_create, name='action_create'),
    path('packs/<int:pk>/actions/<int:action_id>/edit/', views.action_edit, name='action_edit'),
    path('packs/<int:pk>/actions/<int:action_id>/toggle/', views.action_toggle, name='action_toggle'),
    path('packs/<int:pk>/actions/<int:action_id>/delete/', views.action_delete, name='action_delete'),

    # gestión del pack
    path('packs/<int:pk>/edit/', views.pack_edit, name='pack_edit'),
    path('packs/<int:pk>/delete/', views.pack_delete, name='pack_delete'),

    # pública por token
    path('q/<str:token>/', views.publico_por_token, name='publico_por_token'),

    # salas de juego
    path("rooms/create/<int:pack_id>/", views.create_room, name="room_create"),
    path("rooms/<slug:code>/", views.room_view, name="room_view"),
]
