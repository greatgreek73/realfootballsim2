def extract_player_id(slot_val):
    """
    ╨г╨╜╨╕╨▓╨╡╤А╤Б╨░╨╗╤М╨╜╨░╤П ╤Д╤Г╨╜╨║╤Ж╨╕╤П, ╨║╨╛╤В╨╛╤А╨░╤П ╨╕╨╖╨▓╨╗╨╡╨║╨░╨╡╤В playerId ╨║╨░╨║ ╤Б╤В╤А╨╛╨║╤Г
    ╨╕╨╖ ╨╗╤О╨▒╨╛╨│╨╛ ╤Д╨╛╤А╨╝╨░╤В╨░ ╤Б╨╗╨╛╤В╨░.
    ╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╤В ╤Б╤В╤А╨╛╨║╤Г (╨╜╨░╨┐╤А╨╕╨╝╨╡╤А "8012") ╨╕╨╗╨╕ None.
    """
    try:
        if isinstance(slot_val, dict):
            # ╨Э╨╛╨▓╤Л╨╣ ╤Д╨╛╤А╨╝╨░╤В
            player_id = slot_val.get("playerId")
            # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╤З╤В╨╛ ╤Н╤В╨╛ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤В╨╡╨╗╤М╨╜╨╛ ╤Б╤В╤А╨╛╨║╨░ ╨╕╨╗╨╕ ╤З╨╕╤Б╨╗╨╛
            return str(player_id) if player_id is not None else None
        if isinstance(slot_val, (str, int)):
            # ╨б╤В╨░╤А╤Л╨╣ ╤Д╨╛╤А╨╝╨░╤В (╨┐╤А╨╛╤Б╤В╨╛ ╤Б╤В╤А╨╛╨║╨░ ╨╕╨╗╨╕ ╤З╨╕╤Б╨╗╨╛)
            return str(slot_val)
        return None
    except (ValueError, TypeError, AttributeError):
        return None
