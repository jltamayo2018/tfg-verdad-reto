from .models import PackCollaborator

def can_edit_pack(user, pack):
    if not user.is_authenticated:
        return False
    if pack.owner_id == user.id:
        return True
    return PackCollaborator.objects.filter(pack=pack, user=user, role=PackCollaborator.EDITOR).exists()
