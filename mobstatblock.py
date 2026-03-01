import random
from typing import Any, Dict, Optional


# maps abbreviated alignment codes from the JSON to full display strings
ALIGNMENT_MAP = {
    'LG': 'Lawful Good',    'LN': 'Lawful Neutral',  'LE': 'Lawful Evil',
    'NG': 'Neutral Good',   'N':  'True Neutral',     'NE': 'Neutral Evil',
    'CG': 'Chaotic Good',   'CN': 'Chaotic Neutral',  'CE': 'Chaotic Evil',
}

# maps die-size keys from the hit_dice JSON field to their integer values
HIT_DIE_KEYS = {'d2': 2, 'd3': 3, 'd4': 4, 'd5': 5, 'd6': 6, 'd7': 7, 'd8': 8, 'd10': 10, 'd12': 12}

# size letter codes from the JSON → approximate height in inches and weight in lbs
# used to populate self.size = [height_inches, weight] to match PC layout
SIZE_DEFAULTS = {
    'T': [12,   5],     # tiny
    'S': [36,  40],     # small
    'M': [66, 150],     # medium (overridden by JSON length/weight when present)
    'L': [96, 400],     # large
    'H': [144, 800],    # huge
    'G': [240, 4000],   # gargantuan
}


def roll_hit_dice(hit_dice: Dict[str, Any]) -> int:          # rolls hp from the hit_dice JSON field
    total = hit_dice.get('+', 0)                             # flat bonus (e.g. the +4 in 8d8+4)
    for key, sides in HIT_DIE_KEYS.items():
        count = hit_dice.get(key, 0)
        for _ in range(count):
            total += random.randrange(1, sides + 1)
    return max(1, total)                                     # minimum 1 hp


def _expand_alignment(raw: Optional[str]) -> str:            # expands abbreviated alignment to full string
    if raw is None:
        return 'True Neutral'
    return ALIGNMENT_MAP.get(raw.strip(), raw)               # falls back to raw string if not in map


def _parse_size(size_data: Optional[Dict[str, Any]]) -> list:   # converts size JSON block to [height_inches, weight]
    if not size_data:
        return SIZE_DEFAULTS['M'].copy()
    size_letter = size_data.get('size', 'M')
    defaults = SIZE_DEFAULTS.get(size_letter, SIZE_DEFAULTS['M']).copy()
    length = size_data.get('length')                         # length/height in feet from JSON
    weight = size_data.get('weight')
    dimension = size_data.get('dimension', 'length')
    if length is not None and dimension in ('height', 'length'):
        defaults[0] = int(length * 12)                      # convert feet to inches
    if weight is not None:
        defaults[1] = int(weight)
    return defaults


class MobStatblock:
    """
    Adapter between the monsters.json format produced by mob_statblock_converter.py
    and the Character object layout expected by the rest of the system.

    Usage:
        with open('monsters.json') as f:
            data = json.load(f)
        entry = data['Mind Flayer']['Mind Flayer']
        mob = MobStatblock.from_json(entry, event_bus=bus)  # returns a Character-compatible object

    Or to apply mob stats to an existing Character in place (used by wightify()):
        MobStatblock.apply_to(character, entry)

    All mob units carry both:
        char.hit_dice  — the raw formula dict e.g. {'d8': 8, '+': 4}
        char.hp        — the rolled result for this specific instance
    """

    @staticmethod
    def apply_to(char, entry: Dict[str, Any]) -> None:      # mutates an existing Character with mob stats
        basic    = entry.get('basic_info', {})
        combat   = entry.get('combat', {})
        move     = entry.get('movement', {}).get('movement', {})
        size     = entry.get('size', {}).get('size')
        xp_data  = entry.get('experience_value', {})

        # identity
        char.race          = basic.get('creature_type') or basic.get('name', 'Unknown')
        char.classes       = ['0-level']
        char.display_class = ''
        char.display_level = ''
        char.alignment     = _expand_alignment(basic.get('alignment'))
        char.age[1]        = basic.get('mob_type', '')      # age[1] is the category string shown on the char sheet

        # combat stats — stored directly so calculate_ac() / calculate_thaco() short-circuit
        char.ac    = combat.get('ac')                       # raw AC value (e.g. 5 for a wight)
        char.thac0 = combat.get('thac0')                    # raw THAC0 value (e.g. 15 for a wight)

        # hit dice — store formula and roll hp for this instance (same as pc hp/hp_history pattern)
        hit_dice = combat.get('hit_dice', {})
        char.hit_dice = hit_dice                            # formula preserved for combat engine / display
        char.hp       = roll_hit_dice(hit_dice) if hit_dice else char.hp

        # movement — setting self.movement triggers the short-circuit in class_movement()
        char.movement = move.get('mov', 12)

        # size — converts feet to inches for height to match PC layout
        char.size = _parse_size(size)

        # xp fields — mob units don't level up
        char.xp = 0
        char.next_level = [0, char.race]
        char.level = [0]

        # store full raw entry for reference (special abilities, attacks, xp value, etc.)
        char.mob_data = entry

    @classmethod
    def from_json(cls, entry: Dict[str, Any], event_bus=None):  # returns a fresh Character-compatible object
        from character import Character                          # local import to avoid circular dependency
        char = Character.__new__(Character)                     # bypasses __init__ entirely
        char.event_bus = event_bus
        char.character_name = ''
        char.excess = {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0, 'Cha': 0, 'Com': 0}
        char.attributes = {}                               # sparse — display layer uses .get(attr, 10) fallback
        char.gender = 'unknown'
        char.age = [0, '', '', {}, 0]               # [num, category, max_str, age_adj_dict, max_age]
        char.hp_history = [[]]
        char.hit_dice = {}
        cls.apply_to(char, entry)
        return char

