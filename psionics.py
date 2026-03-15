import random
import math

# Races eligible for psionic ability.
# TODO: migrate to attributemins.csv (race-only column) when CSV refactor lands.
# Covers all sub-types explicitly so race string comparisons are unambiguous.
PSIONIC_RACES = frozenset({
    'Human',
    'Dwarf', 'Hill Dwarf', 'Mountain Dwarf',
    'Halfling', 'Stout Halfling', 'Tallfellow Halfling',
})


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

def is_eligible_race(race: str) -> bool:
    """True if the race can be psionic at all."""
    return race in PSIONIC_RACES


def qualifying_attr_count(int_: int, wis: int, cha: int) -> int:
    """Number of qualifying attributes (Int, Wis, Cha) that exceed 16."""
    return sum(1 for x in (int_, wis, cha) if x > 16)


def eligibility_prob(int_: int, wis: int, cha: int) -> float:
    """
    Probability of psionic ability, floored to nearest whole percent.
    Requires at least one qualifying attribute > 16; returns 0.0 otherwise.
    Formula: 0.01 + max(0, Int-16)*0.025 + max(0, Wis-16)*0.015 + max(0, Cha-16)*0.005
    """
    if qualifying_attr_count(int_, wis, cha) == 0:
        return 0.0
    raw = 0.01 + max(0, int_ - 16) * 0.025 + max(0, wis - 16) * 0.015 + max(0, cha - 16) * 0.005
    return math.floor(raw * 100) / 100      # floor to nearest whole percent


# ---------------------------------------------------------------------------
# Strength calculation
# ---------------------------------------------------------------------------

def psionic_strength_full(psionic_roll: int, int_: int, wis: int, cha: int) -> int:
    """
    Computes full (un-halved) psionic strength from a frozen d100 roll and
    current attribute values.  Always returns an even number (multiplier is
    2**quals, minimum 2 when quals >= 1).

    psionic_roll: the frozen d100 value stored on the character (1-100).
    """
    quals = qualifying_attr_count(int_, wis, cha)
    if quals == 0:
        return 0
    bonuses = max(0, int_ - 12) + max(0, wis - 12) + max(0, cha - 12)
    return (2 ** quals) * (psionic_roll + bonuses)


# ---------------------------------------------------------------------------
# Character-level integration
# ---------------------------------------------------------------------------

def check_and_apply(character) -> bool:
    """
    Run the full psionic eligibility and assignment flow against a Character.
    Called at __init__ (after attributes are finalised) and whenever Int, Wis,
    or Cha changes.

    Returns True if psionic_strength changed (used by the caller to decide
    whether to emit PSIONIC_CHANGED).

    Flow:
      1. Race gate — ineligible races are zeroed and exit immediately.
      2. Already psionic → recompute strength from frozen roll; handle loss if
         quals drop to zero.
      3. Not yet psionic → run probability check; on pass, roll d100, compute
         and store strength.
    """
    int_  = character.attributes['Int']
    wis   = character.attributes['Wis']
    cha   = character.attributes['Cha']
    old_strength = character.psionic_strength

    # --- race gate ---
    if not is_eligible_race(character.race):
        character.psionic_roll     = 0
        character.psionic_strength = 0
        return old_strength != 0    # True only if something actually changed

    quals = qualifying_attr_count(int_, wis, cha)

    # --- already psionic: recompute from frozen roll ---
    if character.psionic_roll > 0:
        if quals == 0:
            # all qualifying attrs have dropped to ≤16 — psionics lost
            character.psionic_roll     = 0
            character.psionic_strength = 0
        else:
            character.psionic_strength = psionic_strength_full(
                character.psionic_roll, int_, wis, cha)
        return character.psionic_strength != old_strength

    # --- not yet psionic: needs at least one qualifying attr ---
    if quals == 0:
        return False                # nothing to check, nothing changed

    # --- probability check ---
    prob = eligibility_prob(int_, wis, cha)
    if random.random() >= prob:
        return False                # didn't pass the check this time

    # --- passed: roll d100, compute and store ---
    character.psionic_roll     = random.randint(1, 100)
    character.psionic_strength = psionic_strength_full(
        character.psionic_roll, int_, wis, cha)
    return True                     # strength changed (was 0, now > 0)


def display_strength(character) -> str:
    """
    Returns the display string for the character sheet 'Psionics:' label.
    Shows the halved value (attack / defence split) or 'none'.
    """
    if character.psionic_strength == 0:
        return 'none'
    return str(character.psionic_strength // 2)
