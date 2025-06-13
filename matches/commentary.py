import random

TEMPLATES = {
    'goal': [
        "GOAL!!! {shooter} ({team})! Score: {home}-{away}",
        "{team}'s {shooter} strikes! {home}-{away} on the scoreboard.",
        "It's in! {shooter} scores for {team}. Score now {home}-{away}.",
    ],
    'shot_miss': [
        "{shooter} shoots but misses the target.",
        "Close attempt from {shooter}, but it goes wide.",
    ],
    'pass': [
        "{player} plays a pass to {recipient} ({from_zone}->{to_zone}).",
        "Pass from {player} to {recipient} moving {from_zone}->{to_zone}.",
    ],
    'foul': [
        "Foul by {player} on {target} in {zone}.",
        "{player} brings down {target} in {zone}.",
    ],
    'dribble': [
        "{player} dribbles toward {zone}.",
        "{player} attempts to beat his man into {zone}.",
    ],
    'interception': [
        "{interceptor} intercepts {player} in {zone}.",
        "Great read by {interceptor}! Steals it from {player} in {zone}.",
    ],
    'counterattack': [
        "Counterattack! {interceptor} takes over.",
        "Quick break as {interceptor} wins the ball!",
    ],
}


def render_comment(event_type: str, **kwargs) -> str:
    """Return a random commentary line for the given event type."""
    variants = TEMPLATES.get(event_type)
    if not variants:
        return ""
    template = random.choice(variants)
    return template.format(**kwargs)
