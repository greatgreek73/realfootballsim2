# players/services/avatar.py
import base64
import hashlib
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile

from openai import OpenAI
from players.models import Player

client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

_STYLES = [
    "studio soft light, neutral grey background, portrait",
    "sports media day lighting, clean backdrop, portrait",
    "stadium tunnel background, shallow depth of field, portrait",
    "training ground background, overcast light, portrait",
    "locker room background, soft cinematic light, portrait",
]
_KIT_COLORS = ["blue kit", "red kit", "green kit", "yellow kit", "white kit", "black kit", "purple kit", "orange kit"]

def _prompt_for_player(p: Player) -> str:
    pos = (p.position or "").lower()
    pos_desc = {
        "gk": "goalkeeper in long-sleeve jersey and gloves",
        "g": "goalkeeper in long-sleeve jersey and gloves",
        "goalkeeper": "goalkeeper in long-sleeve jersey and gloves",
        "defender": "defender",
        "midfielder": "midfielder",
        "forward": "forward",
        "striker": "striker",
    }
    role = pos_desc.get(pos, "football player")

    key = f"{p.id}-{p.first_name}-{p.last_name}".encode("utf-8", "ignore")
    h = int(hashlib.md5(key).hexdigest()[:8], 16)
    style = _STYLES[h % len(_STYLES)]
    kit = _KIT_COLORS[(h // 7) % len(_KIT_COLORS)]

    return (
        f"Professional football {role} headshot, {style}, wearing {kit}, "
        f"looking slightly off-camera, 3/4 view, clean background, "
        f"natural skin tones, game card art, high quality"
    )

def generate_and_save_avatar(player: Player, *, overwrite: bool = False, size: str = "512x512") -> Optional[str]:
    """
    Генерирует аватар через OpenAI и сохраняет в player.avatar.
    Возвращает относительный URL или None при ошибке.
    """
    if not settings.OPENAI_API_KEY or client is None:
        return None

    if player.avatar and not overwrite:
        return player.avatar.url

    prompt = _prompt_for_player(player)

    try:
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            response_format="b64_json",
            n=1,
        )
        b64 = resp.data[0].b64_json
        if not b64:
            return None

        binary = base64.b64decode(b64)
        filename = f"player_{player.id}.png"
        player.avatar.save(filename, ContentFile(binary), save=True)
        return player.avatar.url
    except Exception:
        return None
