import jwt
import time
from django.conf import settings


def generate_jitsi_jwt(
    room_name: str,
    user_id: str,
    display_name: str,
    is_moderator: bool = False,
):
    now = int(time.time())

    payload = {
        "aud": "jitsi",
        "iss": "chat",
        "sub": "8x8.vc",
        "room": room_name,
        "exp": now + 60 * 60,   # 1 hora
        "nbf": now - 10,
        "context": {
            "user": {
                "id": user_id,
                "name": display_name,
                "moderator": is_moderator,
            }
        },
        "features": {
            "livestreaming": False,
            "recording": False,
            "transcription": False,
            "outbound-call": False,
        },
    }

    token = jwt.encode(
        payload,
        settings.JITSI_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": settings.JITSI_KID},
    )

    return token