def extract_player_id(slot_val):
    """
    Универсальная функция, которая извлекает playerId как строку
    из любого формата слота.
    Возвращает строку (например "8012") или None.
    """
    try:
        if isinstance(slot_val, dict):
            # Новый формат
            player_id = slot_val.get("playerId")
            # Проверяем что это действительно строка или число
            return str(player_id) if player_id is not None else None
        elif slot_val is not None:
            # Старый формат (просто строка или число)
            return str(slot_val)
        return None
    except (ValueError, TypeError, AttributeError):
        return None
