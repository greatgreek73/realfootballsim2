import random

TEMPLATES = {
    'goal': [
        "ГОЛ!!! {shooter} ({team})! Счёт: {home}-{away}",
        "{shooter} из команды {team} наносит удар! На табло {home}-{away}.",
        "Мяч в сетке! Гол! {shooter} забивает за {team}. Счёт теперь {home}-{away}.",
    ],
    'shot_miss': [
        "{shooter} бьёт, но мимо ворот.",
        "Опасный момент у {shooter}, но мяч проходит мимо.",
    ],
    'pass': [
        "{player} делает пас на {recipient} ({from_zone}->{to_zone}).",
        "Передача от {player} на {recipient}, продвижение {from_zone}->{to_zone}.",
    ],
    'foul': [
        "Фол со стороны {player} против {target} в зоне {zone}.",
        "{player} сбивает {target} в зоне {zone}.",
    ],
    'dribble': [
        "{player} ведёт мяч к зоне {zone}.",
        "{player} пытается обыграть соперника и войти в {zone}.",
    ],
    'interception': [
        "{interceptor} перехватывает передачу {player} в зоне {zone}.",
        "Отличное чтение игры от {interceptor}! Он отбирает мяч у {player} в зоне {zone}.",
    ],
    'counterattack': [
        "Контратака! {interceptor} начинает атаку.",
        "Быстрый выпад – {interceptor} завладел мячом!",
    ],
}


def render_comment(event_type: str, **kwargs) -> str:
    """Возвращает случайную строку комментария для заданного типа события."""
    variants = TEMPLATES.get(event_type)
    if not variants:
        return ""
    template = random.choice(variants)
    return template.format(**kwargs)
