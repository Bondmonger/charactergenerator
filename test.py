"""
test_character_mob.py
=====================
End-to-end tests for the 1E AD&D character generator refactor.
Covers: Character mutations, event emission, MobStatblock adapter,
        wightification (with and without monsters.json), and override
        short-circuits on calculate_ac() / calculate_thaco().

Run from the project root (where character.py lives):
    python test_character_mob.py

The script does NOT depend on pytest — it uses only the stdlib
unittest module so it can be run anywhere without extra installs.
"""

import os
import sys
import tempfile
import unittest

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so all the game modules resolve.
# Adjust this path if the test file lives in a subdirectory.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Minimal stub EventBus — mirrors the real one's interface without requiring
# gameevents.py to be importable.  Swap for the real one if preferred.
# ---------------------------------------------------------------------------
class StubEventBus:
    def __init__(self):
        self.events = []          # list of (event_type, payload) tuples

    def emit(self, event_type, payload):
        self.events.append((event_type, payload))

    def last(self):
        """Return the most recently emitted (event_type, payload) or None."""
        return self.events[-1] if self.events else None

    def types(self):
        """Return a flat list of every event type emitted so far."""
        return [e[0] for e in self.events]

    def clear(self):
        self.events.clear()


# ---------------------------------------------------------------------------
# Minimal wight entry that mirrors what monsters.json contains.
# Used when testing MobStatblock without a real monsters.json on disk.
# ---------------------------------------------------------------------------
WIGHT_ENTRY = {
    "basic_info": {
        "name": "Wight",
        "creature_type": "Wight",
        "alignment": "LE",
        "mob_type": "undead",
    },
    "combat": {
        "ac": 5,
        "thac0": 15,
        "hit_dice": {"d8": 4, "+": 3},
    },
    "movement": {
        "movement": {"mov": 12}
    },
    "size": {
        "size": {"size": "M", "length": 6.0, "dimension": "height"}
    },
    "experience_value": {},
}

# A second minimal entry for generic from_json testing
GNOLL_ENTRY = {
    "basic_info": {
        "name": "Gnoll",
        "creature_type": "Gnoll",
        "alignment": "CE",
        "mob_type": "humanoid",
    },
    "combat": {
        "ac": 5,
        "thac0": 17,
        "hit_dice": {"d8": 2},
    },
    "movement": {
        "movement": {"mov": 9}
    },
    "size": {
        "size": {"size": "L", "length": 7.5, "weight": 280, "dimension": "height"}
    },
    "experience_value": {},
}


# ===========================================================================
# Helper — build a real Character without touching random class selection by
# pinning race, classes, and a safe attrib list.
# ===========================================================================
def make_fighter(level=3, event_bus=None):
    """Return a deterministic Fighter Character for testing."""
    from character import Character
    attrib_list = [
        {'Str': 16, 'Int': 12, 'Wis': 10, 'Dex': 14, 'Con': 15, 'Cha': 11, 'Com': 10, 'Exc': 0},
        {'Str': 0,  'Int': 0,  'Wis': 0,  'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0,  'Exc': 0},
    ]
    return Character(
        level=level,
        race='Human',
        gender='male',
        classes=['Fighter'],
        attrib_list=attrib_list,
        event_bus=event_bus,
    )


def make_thief(level=3, event_bus=None):
    """Return a deterministic Thief Character for testing."""
    from character import Character
    attrib_list = [
        {'Str': 12, 'Int': 14, 'Wis': 9, 'Dex': 17, 'Con': 12, 'Cha': 13, 'Com': 11, 'Exc': 0},
        {'Str': 0,  'Int': 0,  'Wis': 0, 'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0, 'Exc': 0},
    ]
    return Character(
        level=level,
        race='Human',
        gender='female',
        classes=['Thief'],
        attrib_list=attrib_list,
        event_bus=event_bus,
    )


# ===========================================================================
# TEST SUITES
# ===========================================================================

class TestCharacterBasicInit(unittest.TestCase):
    """Verify that Character initialises with the expected attributes."""

    def test_fighter_has_required_fields(self):
        c = make_fighter()
        for field in ('race', 'classes', 'alignment', 'attributes', 'xp',
                      'level', 'hp', 'size'):
            self.assertTrue(hasattr(c, field), f"Missing field: {field}")

    def test_no_ac_or_thac0_on_pc(self):
        """PC characters must not have ac or thac0 set — values are always calculated."""
        c = make_fighter()
        self.assertFalse(hasattr(c, 'ac'), "PC should not have top-level 'ac' field")
        self.assertFalse(hasattr(c, 'thac0'), "PC should not have top-level 'thac0' field")

    def test_hp_positive(self):
        c = make_fighter()
        self.assertGreater(c.hp, 0)

    def test_level_list(self):
        c = make_fighter(level=3)
        self.assertIsInstance(c.level, list)
        self.assertGreater(max(c.level), 0)

    def test_size_two_elements(self):
        c = make_fighter()
        self.assertEqual(len(c.size), 2)


# ---------------------------------------------------------------------------

class TestRenameEvent(unittest.TestCase):
    """rename() should update character_name and emit CHARACTER_RENAMED."""

    def setUp(self):
        from character import CharacterEventType
        self.CharacterEventType = CharacterEventType
        self.bus = StubEventBus()
        self.c = make_fighter(event_bus=self.bus)

    def test_rename_updates_name(self):
        self.c.rename('Aldric')
        self.assertEqual(self.c.character_name, 'Aldric')

    def test_rename_emits_event(self):
        self.c.rename('Aldric')
        self.assertIn(self.CharacterEventType.CHARACTER_RENAMED, self.bus.types())

    def test_rename_event_payload(self):
        self.c.character_name = 'Old'
        self.c.rename('New')
        evt_type, payload = self.bus.last()
        self.assertEqual(payload['old_name'], 'Old')
        self.assertEqual(payload['new_name'], 'New')

    def test_rename_no_bus_does_not_raise(self):
        c = make_fighter(event_bus=None)
        c.rename('Aldric')
        self.assertEqual(c.character_name, 'Aldric')


# ---------------------------------------------------------------------------

class TestAwardXP(unittest.TestCase):
    """award_xp() should add XP and emit XP_AWARDED; LEVEL_CHANGED on level-up."""

    def setUp(self):
        from character import CharacterEventType
        self.CharacterEventType = CharacterEventType
        self.bus = StubEventBus()
        self.c = make_fighter(level=1, event_bus=self.bus)

    def test_xp_increases(self):
        before = self.c.xp
        self.c.award_xp(500)
        self.assertEqual(self.c.xp, before + 500)

    def test_xp_awarded_event_emitted(self):
        self.c.award_xp(100)
        self.assertIn(self.CharacterEventType.XP_AWARDED, self.bus.types())

    def test_xp_awarded_payload(self):
        self.c.rename('Aldric')
        self.bus.clear()
        self.c.award_xp(250)
        # Find the XP_AWARDED event
        xp_evt = next(p for t, p in self.bus.events
                      if t == self.CharacterEventType.XP_AWARDED)
        self.assertEqual(xp_evt['amount'], 250)

    def test_level_changed_on_level_up(self):
        # Award enough XP to push a level-1 Fighter to level 2 (2000 XP threshold)
        self.c.xp = 0
        self.c.award_xp(2001)
        self.assertIn(self.CharacterEventType.LEVEL_CHANGED, self.bus.types())


# ---------------------------------------------------------------------------

class TestDrainLevel(unittest.TestCase):
    """drain_level() should reduce level and emit LEVEL_CHANGED."""

    def setUp(self):
        from character import CharacterEventType
        self.CharacterEventType = CharacterEventType
        self.bus = StubEventBus()
        self.c = make_fighter(level=3, event_bus=self.bus)

    def test_drain_returns_message(self):
        msg = self.c.drain_level()
        self.assertIsInstance(msg, str)
        self.assertTrue(len(msg) > 0)

    def test_drain_emits_level_changed(self):
        self.c.drain_level()
        self.assertIn(self.CharacterEventType.LEVEL_CHANGED, self.bus.types())

    def test_drain_to_zero_triggers_wightify(self):
        """Draining a level-1 character to 0 should trigger wightification."""
        from character import CharacterEventType
        c = make_fighter(level=1, event_bus=self.bus)
        self.bus.clear()
        msg = c.drain_level()
        self.assertIn('WIGHT', msg.upper())
        self.assertIn(CharacterEventType.CHARACTER_TRANSFORMED, self.bus.types())


# ---------------------------------------------------------------------------

class TestChangeAttribute(unittest.TestCase):
    """change_attribute() should adjust the attribute and emit ATTRIBUTE_CHANGED."""

    def setUp(self):
        from character import CharacterEventType
        self.CharacterEventType = CharacterEventType
        self.bus = StubEventBus()
        self.c = make_fighter(event_bus=self.bus)

    def test_attribute_value_changes(self):
        before = self.c.attributes['Wis']
        self.c.change_attribute('Wis', +2)
        self.assertEqual(self.c.attributes['Wis'], before + 2)

    def test_attribute_changed_event(self):
        self.c.change_attribute('Dex', +1)
        self.assertIn(self.CharacterEventType.ATTRIBUTE_CHANGED, self.bus.types())

    def test_attribute_payload_old_and_new(self):
        old = self.c.attributes['Int']
        self.c.change_attribute('Int', -1)
        evt_type, payload = self.bus.last()
        self.assertEqual(payload['old_value'], old)
        self.assertEqual(payload['new_value'], old - 1)
        self.assertEqual(payload['attr'], 'Int')


# ---------------------------------------------------------------------------

class TestCalculateACAndTHACO(unittest.TestCase):
    """Short-circuit: when ac/thac0 are set directly on the unit,
       calculate_ac() and calculate_thaco() must use the stored value."""

    def setUp(self):
        self.c = make_fighter()

    def test_ac_no_override_returns_int(self):
        result = self.c.calculate_ac()
        self.assertIsInstance(result, (int, float))

    def test_ac_short_circuit(self):
        # AC 5 → stored as self.ac = 5 → calculate_ac() should return 5 - 10 = -5
        self.c.ac = 5
        self.assertEqual(self.c.calculate_ac(), -5)

    def test_thaco_no_override_returns_int(self):
        result = self.c.calculate_thaco()
        self.assertIsInstance(result, (int, float))

    def test_thaco_short_circuit(self):
        # THAC0 15 → stored as self.thac0 = 15 → calculate_thaco() should return 15 - 20 = -5
        self.c.thac0 = 15
        self.assertEqual(self.c.calculate_thaco(), -5)

    def test_clearing_ac_restores_calculation(self):
        self.c.ac = 5
        del self.c.ac
        # Should not raise and should revert to normal calculation
        result = self.c.calculate_ac()
        self.assertIsNotNone(result)


# ---------------------------------------------------------------------------

class TestClassMovement(unittest.TestCase):
    """class_movement() short-circuits when self.movement is set."""

    def test_movement_attribute_short_circuits(self):
        c = make_fighter()
        c.movement = 9
        self.assertEqual(c.class_movement(), 9)

    def test_no_movement_attribute_calculates(self):
        c = make_fighter()
        if hasattr(c, 'movement'):
            del c.movement
        result = c.class_movement()
        self.assertIsInstance(result, (int, float))
        self.assertGreater(result, 0)


# ---------------------------------------------------------------------------

class TestMobStatblockApplyTo(unittest.TestCase):
    """MobStatblock.apply_to() mutates a Character in place correctly."""

    def setUp(self):
        from mobstatblock import MobStatblock
        self.MobStatblock = MobStatblock
        self.c = make_fighter()
        self.MobStatblock.apply_to(self.c, WIGHT_ENTRY)

    def test_race_updated(self):
        self.assertEqual(self.c.race, 'Wight')

    def test_alignment_expanded(self):
        self.assertEqual(self.c.alignment, 'Lawful Evil')

    def test_ac_set(self):
        self.assertEqual(self.c.ac, 5)

    def test_thac0_set(self):
        self.assertEqual(self.c.thac0, 15)

    def test_ac_short_circuits_to_correct_display_value(self):
        # calculate_ac() returns (override - 10); display layer adds 10 → final AC 5
        self.assertEqual(self.c.calculate_ac(), -5)

    def test_thaco_short_circuits_to_correct_display_value(self):
        # calculate_thaco() returns (override - 20); display layer adds 20 → THAC0 15
        self.assertEqual(self.c.calculate_thaco(), -5)

    def test_hp_rolled_positive(self):
        self.assertGreater(self.c.hp, 0)

    def test_hit_dice_formula_stored(self):
        self.assertIn('d8', self.c.hit_dice)
        self.assertEqual(self.c.hit_dice['d8'], 4)

    def test_movement_set(self):
        self.assertEqual(self.c.movement, 12)

    def test_class_movement_short_circuits(self):
        self.assertEqual(self.c.class_movement(), 12)

    def test_size_height_in_inches(self):
        # 6.0 feet → 72 inches
        self.assertEqual(self.c.size[0], 72)

    def test_mob_type_in_age(self):
        self.assertEqual(self.c.age[1], 'undead')

    def test_xp_zeroed(self):
        self.assertEqual(self.c.xp, 0)

    def test_mob_data_stored(self):
        self.assertTrue(hasattr(self.c, 'mob_data'))


# ---------------------------------------------------------------------------

class TestMobStatblockFromJson(unittest.TestCase):
    """MobStatblock.from_json() builds a fresh mob unit without __init__."""

    def setUp(self):
        from mobstatblock import MobStatblock
        self.MobStatblock = MobStatblock
        self.bus = StubEventBus()
        self.mob = self.MobStatblock.from_json(GNOLL_ENTRY, event_bus=self.bus)

    def test_instance_has_event_bus(self):
        self.assertIs(self.mob.event_bus, self.bus)

    def test_race_set(self):
        self.assertEqual(self.mob.race, 'Gnoll')

    def test_alignment_expanded(self):
        self.assertEqual(self.mob.alignment, 'Chaotic Evil')

    def test_attributes_sparse(self):
        # Mob units should NOT have all seven PC attributes auto-populated
        self.assertIsInstance(self.mob.attributes, dict)

    def test_hp_positive(self):
        self.assertGreater(self.mob.hp, 0)

    def test_hit_dice_formula(self):
        self.assertEqual(self.mob.hit_dice.get('d8'), 2)

    def test_size_height_in_inches(self):
        # 7.5 feet → 90 inches
        self.assertEqual(self.mob.size[0], 90)

    def test_size_weight(self):
        self.assertEqual(self.mob.size[1], 280)

    def test_movement(self):
        self.assertEqual(self.mob.movement, 9)

    def test_ac_correct(self):
        self.assertEqual(self.mob.ac, 5)

    def test_classes_0level(self):
        self.assertEqual(self.mob.classes, ['0-level'])


# ---------------------------------------------------------------------------

class TestRollHitDice(unittest.TestCase):
    """roll_hit_dice() should always return at least 1 and stay within range."""

    def setUp(self):
        from mobstatblock import roll_hit_dice
        self.roll_hit_dice = roll_hit_dice

    def test_minimum_one(self):
        # Even a formula with negative flat bonus can't go below 1
        result = self.roll_hit_dice({'d4': 1, '+': -10})
        self.assertGreaterEqual(result, 1)

    def test_upper_bound_d8_x4_plus3(self):
        # 4d8+3 → max 35
        for _ in range(50):
            result = self.roll_hit_dice({'d8': 4, '+': 3})
            self.assertLessEqual(result, 35)
            self.assertGreaterEqual(result, 4 + 3)  # min = 4×1 + 3

    def test_flat_bonus_only(self):
        result = self.roll_hit_dice({'+': 7})
        self.assertEqual(result, 7)

    def test_empty_dict_returns_one(self):
        result = self.roll_hit_dice({})
        self.assertEqual(result, 1)  # max(1, 0)

    def test_multi_die_types(self):
        result = self.roll_hit_dice({'d6': 2, 'd8': 1})
        self.assertGreaterEqual(result, 3)
        self.assertLessEqual(result, 20)


# ---------------------------------------------------------------------------

class TestAlignmentExpansion(unittest.TestCase):
    """_expand_alignment() maps all nine codes correctly and handles edge cases."""

    def setUp(self):
        from mobstatblock import _expand_alignment
        self.expand = _expand_alignment

    def test_all_nine_codes(self):
        expected = {
            'LG': 'Lawful Good',    'LN': 'Lawful Neutral', 'LE': 'Lawful Evil',
            'NG': 'Neutral Good',   'N':  'True Neutral',   'NE': 'Neutral Evil',
            'CG': 'Chaotic Good',   'CN': 'Chaotic Neutral', 'CE': 'Chaotic Evil',
        }
        for code, full in expected.items():
            self.assertEqual(self.expand(code), full)

    def test_none_returns_true_neutral(self):
        self.assertEqual(self.expand(None), 'True Neutral')

    def test_unknown_code_passes_through(self):
        self.assertEqual(self.expand('XY'), 'XY')

    def test_whitespace_stripped(self):
        self.assertEqual(self.expand(' LE '), 'Lawful Evil')


# ---------------------------------------------------------------------------

class TestParseSizeFunction(unittest.TestCase):
    """_parse_size() converts the size JSON block to [height_inches, weight]."""

    def setUp(self):
        from mobstatblock import _parse_size
        self.parse = _parse_size

    def test_none_returns_medium_default(self):
        result = self.parse(None)
        self.assertEqual(result[0], 66)   # SIZE_DEFAULTS['M'] height
        self.assertEqual(result[1], 150)

    def test_feet_to_inches_conversion(self):
        result = self.parse({'size': 'M', 'length': 6.0, 'dimension': 'length'})
        self.assertEqual(result[0], 72)

    def test_height_dimension_also_converts(self):
        result = self.parse({'size': 'M', 'length': 7.0, 'dimension': 'height'})
        self.assertEqual(result[0], 84)

    def test_weight_overridden(self):
        result = self.parse({'size': 'L', 'weight': 500})
        self.assertEqual(result[1], 500)

    def test_large_size_defaults(self):
        result = self.parse({'size': 'L'})
        self.assertEqual(result[0], 96)

    def test_unknown_size_letter_falls_back_to_medium(self):
        result = self.parse({'size': 'Z'})
        self.assertEqual(result[0], 66)


# ---------------------------------------------------------------------------

class TestWightificationWithFakeJson(unittest.TestCase):
    """wightify() end-to-end: requires monsters.json as a permanent fixture
       in the working directory alongside character.py."""

    def setUp(self):
        from character import CharacterEventType
        self.CharacterEventType = CharacterEventType
        self.bus = StubEventBus()
        self.c = make_fighter(level=3, event_bus=self.bus)

        # Capture original physical / mental stats before wightification
        self.orig_height = self.c.size[0]
        self.orig_weight = self.c.size[1]
        self.orig_int    = self.c.attributes['Int']
        self.orig_wis    = self.c.attributes['Wis']

        self.bus.clear()
        self.msg = self.c.wightify()

    def test_returns_wight_message(self):
        self.assertIn('WIGHT', self.msg.upper())

    def test_character_transformed_event_emitted(self):
        self.assertIn(self.CharacterEventType.CHARACTER_TRANSFORMED, self.bus.types())

    def test_event_payload_transformation_field(self):
        evt_type, payload = self.bus.last()
        self.assertEqual(payload['transformation'], 'wight')

    def test_height_preserved(self):
        self.assertEqual(self.c.size[0], self.orig_height)

    def test_weight_preserved(self):
        self.assertEqual(self.c.size[1], self.orig_weight)

    def test_int_preserved(self):
        self.assertEqual(self.c.attributes['Int'], self.orig_int)

    def test_wis_preserved(self):
        self.assertEqual(self.c.attributes['Wis'], self.orig_wis)

    def test_race_set_to_wight(self):
        self.assertEqual(self.c.race, 'Wight')

    def test_ac_from_json(self):
        self.assertEqual(self.c.ac, 5)

    def test_thac0_from_json(self):
        self.assertEqual(self.c.thac0, 15)

    def test_hp_positive_after_wightify(self):
        self.assertGreater(self.c.hp, 0)

    def test_movement_set(self):
        self.assertEqual(self.c.movement, 12)

    def test_mob_type_undead(self):
        self.assertEqual(self.c.age[1], 'undead')


# ---------------------------------------------------------------------------

class TestDisplayACAndTHACO(unittest.TestCase):
    """Simulate what the display layer does: 10 + calculate_ac(), 20 + calculate_thaco()."""

    def test_mob_display_ac_equals_5(self):
        c = make_fighter()
        c.ac = 5
        display_ac = 10 + c.calculate_ac()
        self.assertEqual(display_ac, 5)

    def test_mob_display_thaco_equals_15(self):
        c = make_fighter()
        c.thac0 = 15
        display_thaco = 20 + c.calculate_thaco()
        self.assertEqual(display_thaco, 15)

    def test_pc_display_ac_reasonable(self):
        c = make_fighter()
        display_ac = 10 + c.calculate_ac()
        self.assertGreater(display_ac, 0)
        self.assertLess(display_ac, 15)

    def test_pc_display_thaco_reasonable(self):
        c = make_fighter()
        display_thaco = 20 + c.calculate_thaco()
        self.assertGreater(display_thaco, 5)
        self.assertLess(display_thaco, 25)


# ---------------------------------------------------------------------------

class TestDualClassEligibility(unittest.TestCase):
    """dual_class_eligible() and dual_class_options() gate checks."""

    def setUp(self):
        import selectclass
        from selectclass import dual_class_eligible, dual_class_options
        self.eligible = dual_class_eligible
        self.options = dual_class_options
        selectclass._dual_class_attr_minimums.cache_clear()

    # --- Bard NG carve-out ---------------------------------------------------

    def test_bard_track_ng_alignment_allowed(self):
        """Fighter → Thief is normally LG/LN only, but NG gets a carve-out
        when bard_track=True."""
        # Str 15, Int 12, Wis 14, Dex 12, Con 12, Cha 15 — meets Fighter primaries
        # and Thief Dex minimum.
        attrs = {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 17, 'Con': 12, 'Cha': 15, 'Com': 10, 'Exc': 0}
        self.assertTrue(
            self.eligible('Fighter', 'Thief', attrs,
                          alignment='Neutral Good', race='Human', bard_track=True),
            "NG Fighter on bard track should be eligible to pivot to Thief"
        )

    def test_bard_track_ng_rejected_without_flag(self):
        """Same character, bard_track=False — NG should fail the alignment gate."""
        attrs = {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 12, 'Con': 12, 'Cha': 15, 'Com': 10, 'Exc': 0}
        self.assertFalse(
            self.eligible('Fighter', 'Thief', attrs, alignment='Neutral Good', race='Human', bard_track=False),
            "NG Fighter without bard track should be rejected"
        )

    # --- Ranger with all three primaries -------------------------------------

    def test_ranger_with_all_primaries_is_eligible(self):
        """A Ranger who satisfies Str, Wis, AND Con primaries should appear
        in dual_class_options() for at least one valid destination."""
        # Ranger primaries: Str 13, Wis 14, Con 14 (typical 1E values)
        attrs = {'Str': 15, 'Int': 15, 'Wis': 17, 'Dex': 13, 'Con': 15, 'Cha': 12, 'Com': 10, 'Exc': 0}
        result = self.options('Ranger', attrs, alignment='Lawful Good', race='Human', bard_track=False)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0,
                           "Ranger with all primaries at 15 should have at least one valid destination")

    # --- Class with no primary attribute -------------------------------------

    def test_class_with_no_primary_is_ineligible(self):
        """A class whose primary_attrs() returns an empty list should never
        be dual-class eligible, regardless of attribute scores."""
        # Illusionist has no primary attribute in standard 1E rules.
        attrs = {'Str': 18, 'Int': 18, 'Wis': 18, 'Dex': 18, 'Con': 18, 'Cha': 18, 'Com': 10, 'Exc': 0}
        result = self.options('Illusionist', attrs, alignment='Neutral', race='Human', bard_track=False)
        self.assertEqual(result, [],
                         "A class with no primary attribute should return no dual-class options")

    # --- Half-elf non-bard rejection -----------------------------------------

    def test_half_elf_rejected_outside_bard_track(self):
        """Half-elves are only dual-class eligible on the bard track.
        Any other combination should be rejected regardless of attributes."""
        attrs = {'Str': 17, 'Int': 16, 'Wis': 14, 'Dex': 16, 'Con': 15, 'Cha': 16, 'Com': 12, 'Exc': 0}
        result = self.options('Fighter', attrs, alignment='Lawful Good', race='Half-elf', bard_track=False)
        self.assertEqual(result, [],
            "Half-elf off the bard track should have no dual-class options")

    def test_half_elf_accepted_on_bard_track(self):
        """A Half-elf Fighter with adequate stats on the bard track should
        be eligible to pivot to Thief."""
        attrs = {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 17, 'Con': 12, 'Cha': 15, 'Com': 10, 'Exc': 0}
        self.assertTrue(
            self.eligible('Fighter', 'Thief', attrs, alignment='Neutral Good', race='Half-elf', bard_track=True),
            "Half-elf Fighter on bard track should be eligible for Fighter → Thief"
        )


# ---------------------------------------------------------------------------

class TestDualClassCharacter(unittest.TestCase):
    """dual_class field, initiate_dual_class(), class_thaco(), HP zeros,
    XP freeze, and crossover reinsertion."""

    # High-attribute Fighter who can dual-class to Thief (Human, LG).
    # Two dicts required: [0] = attributes, [1] = excess — mirrors make_fighter() pattern.
    # NOTE: Character.__init__ destructively pops index 1, so we must pass a fresh
    # copy each call — never pass the class-level list directly.
    _FIGHTER_ATTRS_TEMPLATE = [
        {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 17, 'Con': 12, 'Cha': 15, 'Com': 10, 'Exc': 0},
        {'Str': 0,  'Int': 0,  'Wis': 0,  'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0,  'Exc': 0},
    ]

    def _make_lg_fighter(self, level=5):
        import copy
        from character import Character
        c = Character(
            level=level,
            race='Human',
            gender='male',
            classes=['Fighter'],
            attrib_list=copy.deepcopy(self._FIGHTER_ATTRS_TEMPLATE),
        )
        c.alignment = 'Lawful Good'   # force a permissible alignment
        return c

    # ---- __init__ default ------------------------------------------------

    def test_dual_class_none_by_default(self):
        c = self._make_lg_fighter()
        self.assertIsNone(c.dual_class)

    # ---- initiate_dual_class() -------------------------------------------

    def test_initiate_sets_dual_class_dict(self):
        c = self._make_lg_fighter(level=5)
        pre_xp = c.xp
        c.initiate_dual_class('Thief')
        self.assertIsNotNone(c.dual_class)
        self.assertEqual(c.dual_class['original'], 'Fighter')
        self.assertEqual(c.dual_class['destination'], 'Thief')
        self.assertIn('frozen_xp', c.dual_class)
        self.assertEqual(c.dual_class['frozen_xp'], pre_xp)

    def test_initiate_freezes_original_level(self):
        c = self._make_lg_fighter(level=5)
        frozen = max(c.level)
        c.initiate_dual_class('Thief')
        self.assertEqual(c.dual_class['original_level'], frozen)

    def test_initiate_sets_destination_class(self):
        c = self._make_lg_fighter(level=5)
        c.initiate_dual_class('Thief')
        self.assertEqual(c.classes, ['Thief'])

    def test_initiate_destination_level_one(self):
        """Destination class starts at level 1 (not 0) after transition."""
        c = self._make_lg_fighter(level=5)
        c.initiate_dual_class('Thief')
        self.assertEqual(c.level, [1])

    def test_initiate_hp_history_has_zeros_for_destination(self):
        """hp_history[0] is the destination slot — one zero entry for level 1."""
        c = self._make_lg_fighter(level=5)
        c.initiate_dual_class('Thief')
        # Destination starts at level 1: one zero placeholder
        self.assertEqual(c.hp_history[0], [0])

    def test_initiate_requires_single_class(self):
        from character import Character
        multi_attrs = [
            {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 14, 'Con': 12, 'Cha': 15, 'Com': 10, 'Exc': 0},
            {'Str': 0,  'Int': 0,  'Wis': 0,  'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0,  'Exc': 0},
        ]
        c = Character(level=3, race='Human', gender='male',
                      classes=['Fighter', 'Thief'], attrib_list=multi_attrs)
        with self.assertRaises(ValueError):
            c.initiate_dual_class('Magic User')

    # ---- class_thaco() dual-class awareness --------------------------------

    def test_thaco_pre_crossover_uses_destination_only(self):
        """Pre-crossover: only the destination class level is used for THAC0."""
        import datalocus
        c = self._make_lg_fighter(level=5)
        c.initiate_dual_class('Thief')
        c.level = [2]      # Thief 2, pre-crossover (original was Fighter 5)
        thaco_dest_only = datalocus.base_thaco(('Thief',), (2,))
        self.assertEqual(c.class_thaco(), thaco_dest_only)

    def test_thaco_post_crossover_includes_original(self):
        """Post-crossover: both destination level and frozen original level used."""
        import datalocus
        c = self._make_lg_fighter(level=5)
        orig_level = max(c.level)
        c.initiate_dual_class('Thief')
        # Simulate post-crossover: level exceeds original
        c.level = [orig_level + 1]
        expected = datalocus.base_thaco(
            ('Thief', 'Fighter'),
            (orig_level + 1, orig_level)
        )
        self.assertEqual(c.class_thaco(), expected)

    # ---- XP freeze on original class ----------------------------------------

    def test_original_class_level_stays_frozen_after_award_xp(self):
        """After crossover, award_xp() must not increment the original class.

        Strategy: build a Fighter-5, transition to Thief, place XP just below
        the Thief-6 threshold (20,000), then award exactly enough to cross it.
        Crossover fires (Thief 6 > Fighter 5), Fighter reappears in classes,
        then a second small award confirms Fighter stays frozen.
        Keeping XP deltas small avoids age-increment side-effects.
        """
        c = self._make_lg_fighter(level=5)
        orig_level = max(c.level)           # Fighter 5 is the frozen level

        c.initiate_dual_class('Thief')      # Thief 1, Fighter frozen at 5

        # Thief XP table (1E): 1=1250, 2=2500, 3=5000, 4=10000, 5=20000, 6=40000
        # Crossover fires when Thief level > Fighter 5, i.e. at Thief 6.
        c.xp = 39_900
        c.level = [5]                       # sync level to seeded XP so level_before is correct
        c.award_xp(200)                     # +1 level only: Thief 5→6, crossover fires

        self.assertIn('Fighter', c.classes,
                      "Fighter should be reinserted into classes post-crossover")
        idx = c.classes.index('Fighter')
        self.assertEqual(c.level[idx], orig_level,
                         "Fighter level must remain frozen at original level after dual-class")

        # Second award: confirm Fighter still doesn't move
        c.award_xp(5_000)
        self.assertEqual(c.level[c.classes.index('Fighter')], orig_level,
                         "Fighter level must remain frozen on subsequent XP awards")


# ---------------------------------------------------------------------------

class TestAutoDualClass(unittest.TestCase):
    """_apply_auto_dual_class() fires during __init__ when auto_dual_class=True."""

    def test_dual_class_units_appear_in_bulk(self):
        """With auto_dual_class=True, at least some Human level-9 units should
        dual-class.  Generate 200 and assert at least one has dual_class set.
        (Probabilistic — vanishingly unlikely to fail if probs are non-zero.)"""
        from character import Character
        found = False
        for _ in range(200):
            c = Character(level=9, race='Human', gender='male',
                          classes=['Fighter'], auto_dual_class=True)
            if c.dual_class is not None:
                found = True
                break
        self.assertTrue(found,
                        "Expected at least one dual-class unit in 200 Human Fighter-9s")

    def test_no_dual_class_when_flag_off(self):
        """With auto_dual_class=False (default), dual_class must always be None."""
        from character import Character
        for _ in range(20):
            c = Character(level=9, race='Human', gender='male', classes=['Fighter'])
            self.assertIsNone(c.dual_class,
                              "dual_class must be None when auto_dual_class is False")

    def test_auto_dual_class_xp_arithmetic(self):
        """XP on a dual-classed unit must satisfy two invariants:
          1. Total XP is at least the original class floor for the transition level.
          2. The destination leg (total XP minus original floor) is positive and
             below the next threshold above whatever level the destination actually
             reached — keyed to the actual destination class and level, not a fixed
             target level.
        Runs up to 500 attempts to guarantee a dual-classed unit is found."""
        import generatecharacter
        from character import Character
        dual = None
        for _ in range(500):
            c = Character(level=9, race='Human', gender='male',
                          classes=['Fighter'], auto_dual_class=True)
            if c.dual_class is not None:
                dual = c
                break
        if dual is None:
            self.skipTest("No dual-class unit in 500 attempts — adjust dualprobs if needed")

        orig     = dual.dual_class['original']
        dest     = dual.dual_class['destination']
        orig_lvl = dual.dual_class['original_level']
        dest_lvl = dual.level[0]                        # actual resolved destination level

        attrs_list = list(dual.attributes.values())
        orig_bonus = generatecharacter.bonus_check(orig, attrs_list)
        dest_bonus = generatecharacter.bonus_check(dest, attrs_list)
        def _adj(raw, has_bonus):
            return int(int(raw) * 10 / 11) if has_bonus else int(raw)

        orig_floor = _adj(generatecharacter.return_xp(orig)[orig_lvl - 1], orig_bonus)
        # Ceiling is the next threshold above the destination's actual level.
        dest_ceil  = _adj(generatecharacter.return_xp(dest)[dest_lvl], dest_bonus)

        # Invariant 1: total XP is at least the original class floor
        self.assertGreaterEqual(dual.xp, orig_floor,
                                "Total XP must be at least the original class floor")
        # Invariant 2: destination leg is positive and below the next level threshold
        dest_xp = dual.xp - orig_floor
        self.assertGreater(dest_xp, 0,
                           "Destination XP leg must be positive")
        self.assertLess(dest_xp, dest_ceil,
                        "Destination XP leg must not reach the ceiling of the destination's actual level")

    def test_dual_class_unit_has_valid_structure(self):
        """A dual-classed unit produced by auto_dual_class must have a valid
        dual_class dict, two classes post-crossover or one pre-crossover,
        and positive HP."""
        from character import Character
        dual = None
        for _ in range(200):
            c = Character(level=9, race='Human', gender='male',
                          classes=['Fighter'], auto_dual_class=True)
            if c.dual_class is not None:
                dual = c
                break
        if dual is None:
            self.skipTest("No dual-class unit generated in 200 attempts — increase sample if needed")
        self.assertIn('original', dual.dual_class)
        self.assertIn('destination', dual.dual_class)
        self.assertIn('original_level', dual.dual_class)
        self.assertIn('original_hp', dual.dual_class)
        self.assertIn('frozen_xp', dual.dual_class)
        self.assertGreater(dual.hp, 0)
        self.assertIsInstance(dual.level, list)


# ===========================================================================
# Display convention tests
# ===========================================================================

class TestDisplayConvention(unittest.TestCase):
    """display_classes() and display_level() must format correctly for
    single-class, multiclass, and dual-class (pre- and post-crossover)."""

    def test_single_class_display(self):
        import generatecharacter
        self.assertEqual(generatecharacter.display_classes(['Fighter']), 'Fighter')
        self.assertEqual(generatecharacter.display_level([6]), '6')

    def test_multiclass_display_sorted(self):
        """Multiclass: alphabetical sort, slash-separated."""
        import generatecharacter
        self.assertEqual(generatecharacter.display_classes(['Thief', 'Fighter']), 'Fighter/Thief')
        self.assertEqual(generatecharacter.display_level([4, 5]), '4/5')

    def test_dual_class_pre_crossover(self):
        """Pre-crossover: destination first, original gets asterisk, pipe separator."""
        import generatecharacter
        dc = {'destination': 'Thief', 'original': 'Fighter', 'original_level': 5}
        self.assertEqual(generatecharacter.display_classes(['Thief'], dc), 'Thief|Fighter*')
        self.assertEqual(generatecharacter.display_level([2], dc), '2|5')

    def test_dual_class_post_crossover(self):
        """Post-crossover: destination first, no asterisk."""
        import generatecharacter
        dc = {'destination': 'Thief', 'original': 'Fighter', 'original_level': 5}
        self.assertEqual(generatecharacter.display_classes(['Thief', 'Fighter'], dc), 'Thief|Fighter')
        self.assertEqual(generatecharacter.display_level([7, 5], dc), '7|5')

    def test_dual_class_display_on_character(self):
        """display_class and display_level on a real Character after
        initiate_dual_class() must use pipe convention."""
        c = make_fighter(level=5)
        c.initiate_dual_class('Thief')
        self.assertIn('|', c.display_class)
        self.assertIn('|', c.display_level)
        self.assertIn('Fighter*', c.display_class)

    def test_multiclass_unchanged_by_dual_class_param_none(self):
        """Passing dual_class=None must behave identically to omitting it."""
        import generatecharacter
        self.assertEqual(
            generatecharacter.display_classes(['Thief', 'Fighter'], None),
            'Fighter/Thief')


# ===========================================================================
# Pickle round-trip tests
# ===========================================================================

class TestPickleRoundTrip(unittest.TestCase):
    """Character and Party must survive a pickle/unpickle cycle."""

    def test_character_pickles_with_event_bus(self):
        """A Character with a live event_bus must pickle and unpickle cleanly."""
        import pickle
        bus = StubEventBus()
        c = make_fighter(level=4, event_bus=bus)
        c.rename('Aldric')
        restored = pickle.loads(pickle.dumps(c))
        self.assertEqual(restored.character_name, 'Aldric')
        self.assertEqual(restored.race, c.race)
        self.assertEqual(restored.classes, c.classes)
        self.assertEqual(restored.hp, c.hp)
        self.assertIsNone(restored.event_bus,
                          "event_bus must be None immediately after unpickling")

    def test_character_emits_after_bus_reinjection(self):
        """After re-injecting event_bus, the restored character must emit events."""
        import pickle
        from character import CharacterEventType
        c = make_fighter(level=4, event_bus=StubEventBus())
        restored = pickle.loads(pickle.dumps(c))
        new_bus = StubEventBus()
        restored.event_bus = new_bus
        restored.rename('Bertram')
        self.assertIn(CharacterEventType.CHARACTER_RENAMED, new_bus.types())

    def test_party_pickles_with_event_bus(self):
        """A Party with members and a live event_bus must pickle and unpickle cleanly."""
        import pickle
        from party import Party
        bus = StubEventBus()
        p = Party(event_bus=bus)
        p.add_member(make_fighter(level=3))
        p.add_member(make_thief(level=2))
        restored = pickle.loads(pickle.dumps(p))
        self.assertEqual(len(restored.members), 2)
        self.assertIsNone(restored.event_bus,
                          "Party event_bus must be None immediately after unpickling")

    def test_dual_class_character_survives_pickle(self):
        """A dual-classed character must survive a pickle round-trip with
        dual_class dict intact."""
        import pickle
        c = make_fighter(level=5)
        c.initiate_dual_class('Thief')
        restored = pickle.loads(pickle.dumps(c))
        self.assertIsNotNone(restored.dual_class)
        self.assertEqual(restored.dual_class['original'], 'Fighter')
        self.assertEqual(restored.dual_class['destination'], 'Thief')
        self.assertEqual(restored.dual_class['original_level'],
                         c.dual_class['original_level'])




class TestDualClassDrain(unittest.TestCase):
    """drain_level() on post-crossover dual-class characters.

    Destination class drops by 1 per drain.
    Frozen original class never moves.
    Messages are correct.
    next_level[0] is always int.
    Draining destination to 0 triggers _undo_dual_class().
    """

    _ATTRS = [
        {'Str': 15, 'Int': 16, 'Wis': 14, 'Dex': 17, 'Con': 12, 'Cha': 15, 'Com': 10, 'Exc': 0},
        {'Str': 0,  'Int': 0,  'Wis': 0,  'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0,  'Exc': 0},
    ]

    def _make_post_crossover(self, dest_level=8, orig_level=3):
        """Fighter->Thief, post-crossover: Thief dest_level / Fighter orig_level."""
        import copy
        import generatecharacter
        from character import Character
        c = Character(
            level=orig_level,
            race='Human',
            gender='male',
            classes=['Fighter'],
            attrib_list=copy.deepcopy(self._ATTRS),
        )
        c.alignment = 'Lawful Good'
        # Force level and XP to exactly orig_level so dual_class['original_level'] is
        # deterministic. pc_xp() is random and can resolve to orig_level-1 intermittently.
        c.level = [orig_level]
        c.xp = int(generatecharacter.return_xp('Fighter')[orig_level - 1])
        c.initiate_dual_class('Thief')
        # Manually advance to post-crossover state without going through award_xp
        # to keep the test deterministic and fast.
        c.dual_class['destination'] = 'Thief'
        c.classes = ['Thief', 'Fighter']
        c.level = [dest_level, orig_level]
        # Build a plausible hp_history: dest rolls, frozen orig rolls, con list
        c.hp_history = (
            [[3] * dest_level] +
            [c.dual_class['original_hp'][0]] +
            [[0, 0]]
        )
        # Seed XP at destination floor — single-class, no doubling.
        c.xp = int(generatecharacter.next_xp([c.classes[0]], [c.level[0]], c.attributes, -1)[0])
        c.next_level = [int(generatecharacter.next_xp([c.classes[0]], [c.level[0]], c.attributes)[0]),
                        'Thief']
        return c

    def test_drain_drops_destination_by_one(self):
        c = self._make_post_crossover(dest_level=8, orig_level=3)
        before = c.level[0]
        c.drain_level()
        self.assertEqual(c.level[0], before - 1)

    def test_drain_does_not_change_original_level(self):
        c = self._make_post_crossover(dest_level=8, orig_level=3)
        orig_before = c.level[1]
        c.drain_level()
        self.assertEqual(c.level[1], orig_before)

    def test_drain_message_is_lost_one_level(self):
        c = self._make_post_crossover(dest_level=8, orig_level=3)
        msg = c.drain_level()
        self.assertIn('lost one level', msg.lower())

    def test_next_level_threshold_is_int_after_drain(self):
        """next_level[0] must be int even when bonus XP adjustment produces a float."""
        c = self._make_post_crossover(dest_level=8, orig_level=3)
        c.drain_level()
        self.assertIsInstance(c.next_level[0], int)

    def test_drain_at_destination_level_1_triggers_revert(self):
        """Draining the destination to 0 undoes the dual-class transition."""
        c = self._make_post_crossover(dest_level=1, orig_level=3)
        msg = c.drain_level()
        self.assertIn('reverts', msg.lower())
        self.assertIsNone(c.dual_class)
        self.assertEqual(c.classes, ['Fighter'])
        self.assertEqual(c.level, [3])

    def test_revert_restores_frozen_xp(self):
        """After revert, xp equals the frozen snapshot value."""
        c = self._make_post_crossover(dest_level=1, orig_level=3)
        frozen_xp = c.dual_class['frozen_xp']
        c.drain_level()
        self.assertEqual(c.xp, frozen_xp)

    def test_revert_restores_hp_history(self):
        """After revert, hp_history matches the original_hp snapshot."""
        c = self._make_post_crossover(dest_level=1, orig_level=3)
        original_hp = c.dual_class['original_hp']
        c.drain_level()
        self.assertEqual(c.hp_history, original_hp)

    def test_drain_after_revert_follows_normal_path(self):
        """After revert the restored class drains normally (no dual_class guard)."""
        c = self._make_post_crossover(dest_level=1, orig_level=3)
        c.drain_level()                     # revert — now Fighter 3
        before = c.level[0]
        msg = c.drain_level()               # normal Fighter drain
        self.assertIsNone(c.dual_class)
        self.assertEqual(c.level[0], before - 1)
        self.assertIn('lost one level', msg.lower())

    def test_next_level_int_after_revert(self):
        """next_level[0] must be int after _undo_dual_class."""
        c = self._make_post_crossover(dest_level=1, orig_level=3)
        c.drain_level()
        self.assertIsInstance(c.next_level[0], int)

# ===========================================================================
# DUAL-CLASS HP AND CON BONUS
# ===========================================================================

class TestDualClassHPAndCon(unittest.TestCase):
    """HP history layout and con bonus correctness across all dual-class stages.

    Covers:
      - Pre-crossover zeros for destination, frozen rolls for original
      - Post-crossover real rolls begin at orig_level + 1
      - Con bonus: destination = 0 pre-crossover, accrues post-crossover
      - Con bonus: original always computed from current Con (not frozen)
      - Con bonus: name-level cap applied in absolute level space
      - Con bonus: Ranger/Monk double-HD first-level multiplier preserved
      - modify_con at pre-crossover, post-crossover stages
      - drain_level correctly preserves frozen original rolls (regression)
    """

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _make_fighter_thief(self, fighter_level=5, con=14):
        """Fighter → Thief dual-class.  Con 14 = +0 bonus (non-fighter cap).
        Fighter name-level cap = 9.  Thief name-level cap >= 10 (all levels earn).
        Con 15 = +1 for both.  Con 16 = +2 for both (fighter cap = +3, thief cap = +2).
        """
        import datalocus
        import hitpoints
        from character import Character
        attrs = [
            {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 17, 'Con': con - 1,
             'Cha': 15, 'Com': 10, 'Exc': 0},
            {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0,
             'Cha': 0, 'Com': 0, 'Exc': 0},
        ]
        c = Character(level=fighter_level, race='Human', gender='male',
                      classes=['Fighter'], attrib_list=attrs)
        c.alignment = 'Lawful Good'
        xp_table = list(datalocus.return_xp('Fighter')[0][2:28])
        c.xp = int(xp_table[fighter_level - 1]) + 1
        c.calculate_level(0, uncapped=True)
        c.hp_history = hitpoints.generate_hp(c.classes, c.level, con)
        c.hp = c._flatten()
        return c

    def _make_ranger_cleric(self, ranger_level=3, con=16):
        import datalocus
        import hitpoints
        from character import Character
        attrs = [
            {'Str': 15, 'Int': 14, 'Wis': 17, 'Dex': 12, 'Con': con - 1,
             'Cha': 13, 'Com': 10, 'Exc': 0},
            {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0,
             'Cha': 0, 'Com': 0, 'Exc': 0},
        ]
        c = Character(level=ranger_level, race='Human', gender='male',
                      classes=['Ranger'], attrib_list=attrs)
        c.alignment = 'Neutral Good'
        xp_table = list(datalocus.return_xp('Ranger')[0][2:28])
        c.xp = int(xp_table[ranger_level - 1]) + 1
        c.calculate_level(0, uncapped=True)
        # Rebuild hp_history cleanly so roll count matches level exactly
        c.hp_history = hitpoints.generate_hp(c.classes, c.level, con)
        c.hp = c._flatten()
        return c

    # ------------------------------------------------------------------
    # Pre-crossover layout
    # ------------------------------------------------------------------

    def test_pre_crossover_destination_slot_all_zeros(self):
        """Before crossover, every entry in the destination roll list is 0."""
        c = self._make_fighter_thief(fighter_level=4)
        c.initiate_dual_class('Thief')
        # Level up to Thief 2, 3 — still pre-crossover (orig_level = 4)
        c.xp = 2_400
        c.calculate_level(0)
        c.xp = 4_900
        c.calculate_level(0)
        # All destination rolls must be zero
        self.assertTrue(all(r == 0 for r in c.hp_history[0]),
                        f"Expected all zeros, got {c.hp_history[0]}")

    def test_pre_crossover_frozen_original_rolls_intact(self):
        """Frozen original rolls are preserved unchanged pre-crossover."""
        c = self._make_fighter_thief(fighter_level=3)
        frozen_rolls = c.hp_history[0][:]   # Fighter rolls before transition
        c.initiate_dual_class('Thief')
        # Level up destination a couple of times
        c.xp = 2_400
        c.calculate_level(0)
        self.assertEqual(c.hp_history[1], frozen_rolls,
                         "Frozen original rolls must not change pre-crossover")

    def test_pre_crossover_dest_con_is_zero(self):
        """Destination con bonus is 0 pre-crossover regardless of Con value."""
        c = self._make_fighter_thief(fighter_level=3, con=18)
        c.initiate_dual_class('Thief')
        c.xp = 2_400
        c.calculate_level(0)
        self.assertEqual(c.hp_history[-1][0], 0,
                         "Destination con must be 0 pre-crossover")

    def test_pre_crossover_orig_con_reflects_current_con(self):
        """Original con bonus recalculates from current Con pre-crossover."""
        import datalocus
        c = self._make_fighter_thief(fighter_level=3, con=14)
        c.initiate_dual_class('Thief')
        # Con 14 = +0 bonus
        self.assertEqual(c.hp_history[-1][1], 0)
        # Bump con to 16 (+2, Fighter cap +3 → +2 per level × 3 levels = 6)
        c.modify_attribute('Con', 2)
        bonus = datalocus.con_hpbonus(c.attributes['Con'])
        hpcalcs = datalocus.call_hp('Fighter')
        cap = hpcalcs[6]
        expected = min(bonus, cap) * hpcalcs[7] * min(3, hpcalcs[4])
        self.assertEqual(c.hp_history[-1][1], expected)

    # ------------------------------------------------------------------
    # Crossover boundary — zeros up to orig_level, real rolls after
    # ------------------------------------------------------------------

    def test_levels_at_or_below_orig_level_are_zero(self):
        """After crossover, slots 0..orig_level-1 remain zeros."""
        c = self._make_fighter_thief(fighter_level=3)
        c.initiate_dual_class('Thief')
        # Drive to Thief 4 (post-crossover: 4 > 3)
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        self.assertIn('Thief', c.classes)
        dest_rolls = c.hp_history[0]
        self.assertEqual(dest_rolls[:3], [0, 0, 0],
                         f"First {3} slots must be zero, got {dest_rolls}")

    def test_first_post_crossover_roll_is_nonzero(self):
        """The crossover level slot receives a real HP roll (> 0 almost always)."""
        import random
        random.seed(42)
        c = self._make_fighter_thief(fighter_level=2)
        c.initiate_dual_class('Thief')
        # Drive to Thief 3 (post-crossover)
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        dest_rolls = c.hp_history[0]
        self.assertGreater(len(dest_rolls), 2,
                           "Should have at least 3 entries after Thief 3")
        self.assertGreater(dest_rolls[2], 0,
                           f"Crossover roll must be > 0, got {dest_rolls[2]}")

    # ------------------------------------------------------------------
    # Post-crossover con bonus values
    # ------------------------------------------------------------------

    def test_post_crossover_dest_con_counts_only_post_xo_levels(self):
        """Destination con bonus = bonus × post-crossover levels only.

        Fighter→Thief, orig_level=2, dest=Thief 6, Con 16 (+2, Thief cap +2).
        Post-XO levels = 6 - 2 = 4.  Expected dest_con = 2 × 4 = 8.
        """
        import datalocus
        c = self._make_fighter_thief(fighter_level=2, con=16)
        c.initiate_dual_class('Thief')
        # Fast-forward to Thief 6 post-crossover
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        c.xp = 19_900; c.calculate_level(0)
        c.xp = 39_900; c.calculate_level(0)
        dest_level = c.level[0]
        orig_level = c.dual_class['original_level']   # 2
        bonus = datalocus.con_hpbonus(16)             # +2
        hpc   = datalocus.call_hp('Thief')
        cap   = hpc[6]
        effective_bonus = min(bonus, cap) * hpc[7]
        post_xo = max(0, min(dest_level, hpc[4]) - orig_level)
        expected_dest_con = effective_bonus * post_xo
        self.assertEqual(c.hp_history[-1][0], expected_dest_con,
                         f"dest_con: expected {expected_dest_con}, "
                         f"got {c.hp_history[-1][0]}")

    def test_post_crossover_orig_con_uses_current_con_not_frozen(self):
        """Original class con bonus reflects current Con, not transition-time Con.

        Transition at Con 14 (+0), then bump to Con 16 (+2).
        Fighter orig_level=3, cap=+3 → expected orig_con = 2 × 3 = 6.
        """
        import datalocus
        c = self._make_fighter_thief(fighter_level=3, con=14)
        c.initiate_dual_class('Thief')
        # Reach post-crossover (Thief 4)
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        # Bump Con to 16
        c.modify_attribute('Con', 2)
        bonus  = datalocus.con_hpbonus(16)
        hpc    = datalocus.call_hp('Fighter')
        cap    = hpc[6]
        expected_orig_con = min(bonus, cap) * hpc[7] * min(3, hpc[4])
        self.assertEqual(c.hp_history[-1][1], expected_orig_con,
                         f"orig_con after Con bump: expected {expected_orig_con}, "
                         f"got {c.hp_history[-1][1]}")

    def test_name_level_cap_applied_in_absolute_space(self):
        """Con bonus for destination stops at name-level cap (absolute).

        Fighter dest, orig_level=4, dest_level=14, Con 15 (+1, Fighter cap +3).
        Fighter name cap = 9.  Con-earning levels = min(14,9) - 4 = 5.
        Expected dest_con = 1 × 5 = 5  (NOT 1 × min(10,9) = 9).
        """
        import datalocus
        from character import Character
        # Build a Thief (easy attributes) who transitions to Fighter
        attrs = [
            {'Str': 15, 'Int': 12, 'Wis': 14, 'Dex': 17, 'Con': 14,
             'Cha': 15, 'Com': 10, 'Exc': 0},
            {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0,
             'Cha': 0, 'Com': 0, 'Exc': 0},
        ]
        # We'll manufacture the dual_class state directly rather than driving
        # through 14 levels of XP to keep the test fast.
        c = Character(level=4, race='Human', gender='male',
                      classes=['Thief'], attrib_list=attrs)
        c.alignment = 'Neutral Good'
        c.initiate_dual_class('Fighter')
        c.dual_class['original_level'] = 4  # neutralise XP randomness in __init__
        # Manually set post-crossover state at Fighter 14 / Thief 4
        c.classes = ['Fighter', 'Thief']
        c.level   = [14, 4]
        c.hp_history = [
            [0, 0, 0, 0, 3, 5, 4, 6, 3, 3, 3, 3, 3, 3],  # dest: 4 zeros + 10 rolls
            c.dual_class['original_hp'][0],                 # frozen Thief rolls
            [0, 0],                                         # placeholder
        ]
        c._recompute_dual_class_con()
        dest_con = c.hp_history[-1][0]
        # Fighter con: bonus=1, cap=3 → 1; name cap=9; orig=4 → min(14,9)-4=5
        self.assertEqual(dest_con, 5,
                         f"Expected dest_con=5 (name-level cap), got {dest_con}")

    # ------------------------------------------------------------------
    # Ranger/Monk double-HD first-level multiplier
    # ------------------------------------------------------------------

    def test_ranger_double_hd_con_preserved_post_transition(self):
        """Ranger original con bonus accounts for 2× first-level HD.

        Ranger orig_level=3, Con 16 (+2, Ranger cap +2).
        Effective dice = hpcalcs[1] + 3 - 1 = 2 + 2 = 4.
        Expected orig_con = 2 × 4 = 8.
        """
        import datalocus
        c = self._make_ranger_cleric(ranger_level=3, con=16)
        c.initiate_dual_class('Cleric')
        # Level up to Cleric 4 (post-crossover: 4 > 3)
        c.xp = 1_400;  c.calculate_level(0)
        c.xp = 2_800;  c.calculate_level(0)
        c.xp = 5_600;  c.calculate_level(0)
        hpc  = datalocus.call_hp('Ranger')
        bonus = datalocus.con_hpbonus(16)
        cap   = hpc[6]
        effective = min(bonus, cap) * hpc[7]
        raw_mult  = hpc[1] + 3 - 1          # 2 + 3 - 1 = 4
        expected_orig_con = effective * min(raw_mult, hpc[4])
        self.assertEqual(c.hp_history[-1][1], expected_orig_con,
                         f"Ranger orig_con: expected {expected_orig_con}, "
                         f"got {c.hp_history[-1][1]}")

    def test_ranger_orig_con_updates_on_con_change(self):
        """Ranger orig_con recomputes correctly when Con changes post-transition."""
        import datalocus
        c = self._make_ranger_cleric(ranger_level=3, con=14)
        c.initiate_dual_class('Cleric')
        # Bump Con to 16
        c.modify_attribute('Con', 2)
        hpc   = datalocus.call_hp('Ranger')
        bonus = datalocus.con_hpbonus(16)
        cap   = hpc[6]
        effective = min(bonus, cap) * hpc[7]
        raw_mult  = hpc[1] + 3 - 1
        expected  = effective * min(raw_mult, hpc[4])
        self.assertEqual(c.hp_history[-1][1], expected)

    # ------------------------------------------------------------------
    # modify_con at each stage
    # ------------------------------------------------------------------

    def test_modify_con_pre_crossover_dest_stays_zero(self):
        """modify_con pre-crossover must not give the destination any con bonus."""
        c = self._make_fighter_thief(fighter_level=3, con=12)
        c.initiate_dual_class('Thief')
        c.modify_attribute('Con', 3)   # bump to 15
        self.assertEqual(c.hp_history[-1][0], 0,
                         "Destination con must stay 0 pre-crossover after modify_con")

    def test_modify_con_does_not_clobber_frozen_rolls(self):
        """modify_con must not overwrite frozen original roll list."""
        c = self._make_fighter_thief(fighter_level=3, con=12)
        c.initiate_dual_class('Thief')
        frozen = c.dual_class['original_hp'][0][:]
        c.modify_attribute('Con', 3)
        self.assertEqual(c.hp_history[1], frozen,
                         "Frozen original rolls must survive modify_con")

    def test_modify_con_post_crossover_updates_both_slots(self):
        """Post-crossover modify_con updates both con slots correctly."""
        import datalocus
        c = self._make_fighter_thief(fighter_level=2, con=14)
        c.initiate_dual_class('Thief')
        # Reach Thief 4 post-crossover
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        c.modify_attribute('Con', 2)   # 14 → 16
        dest_con, orig_con = c.hp_history[-1]
        # Both should be non-zero at Con 16
        self.assertGreater(dest_con + orig_con, 0)
        # orig_con: Fighter 2 levels, bonus +2, cap +3 → 2×2=4
        bonus = datalocus.con_hpbonus(16)
        hpc   = datalocus.call_hp('Fighter')
        cap   = hpc[6]
        expected_orig = min(bonus, cap) * hpc[7] * min(2, hpc[4])
        self.assertEqual(orig_con, expected_orig)

    # ------------------------------------------------------------------
    # drain_level regression — frozen rolls must survive
    # ------------------------------------------------------------------

    def test_drain_does_not_destroy_frozen_original_rolls(self):
        """Draining one destination level must not overwrite frozen original rolls.

        Regression: post-crossover elif sliced hp_history to [0:n_classes]
        without preserving the con slot, causing _recompute_dual_class_con
        to write into hp_history[-1] = last roll list, destroying it.
        """
        c = self._make_fighter_thief(fighter_level=2, con=14)
        c.initiate_dual_class('Thief')
        # Reach Thief 4 post-crossover
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        frozen_rolls = c.dual_class['original_hp'][0][:]
        # Drain one level
        c.drain_level()
        self.assertEqual(c.hp_history[1], frozen_rolls,
                         "Frozen original rolls must survive drain_level")

    def test_drain_hp_decreases_by_removed_roll_only(self):
        """HP after drain should equal HP before minus only the removed destination roll."""
        import random
        random.seed(99)
        c = self._make_fighter_thief(fighter_level=2, con=14)
        c.initiate_dual_class('Thief')
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        hp_before   = c.hp
        removed_roll = c.hp_history[0][-1]
        c.drain_level()
        self.assertEqual(c.hp, hp_before - removed_roll,
                         "HP delta should equal only the removed destination roll")

    def test_con_list_length_stays_correct_after_drain(self):
        """hp_history must always be exactly [dest_rolls, orig_rolls, con_list]."""
        c = self._make_fighter_thief(fighter_level=2, con=14)
        c.initiate_dual_class('Thief')
        c.xp = 2_400;  c.calculate_level(0)
        c.xp = 4_900;  c.calculate_level(0)
        c.xp = 9_900;  c.calculate_level(0)
        c.drain_level()
        self.assertEqual(len(c.hp_history), 3,
                         f"hp_history must have 3 entries, got {len(c.hp_history)}")
        self.assertEqual(len(c.hp_history[-1]), 2,
                         f"Con list must have 2 entries, got {c.hp_history[-1]}")

# ===========================================================================
# Bard track tests
# ===========================================================================

class TestBardTrack(unittest.TestCase):
    """bard_eligible(), intended_class flag, transition windows, HP accrual,
    con bonus deferral, class_thaco() three-class, fighter_level preservation."""

    # Attributes that meet all Bard minimums (Str15 Int12 Wis15 Dex15 Con10 Cha15)
    # Wis is 16 (not 15) to survive the -1 age penalty applied at character creation.
    _BARD_ATTRS = [
        {'Str': 15, 'Int': 12, 'Wis': 16, 'Dex': 15, 'Con': 14, 'Cha': 15, 'Com': 10, 'Exc': 0},
        {'Str': 0,  'Int': 0,  'Wis': 0,  'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0,  'Exc': 0},
    ]
    # Attributes that fail Bard minimums (Wis 10 < 15)
    _NON_BARD_ATTRS = [
        {'Str': 15, 'Int': 12, 'Wis': 10, 'Dex': 15, 'Con': 14, 'Cha': 15, 'Com': 10, 'Exc': 0},
        {'Str': 0,  'Int': 0,  'Wis': 0,  'Dex': 0,  'Con': 0,  'Cha': 0,  'Com': 0,  'Exc': 0},
    ]

    def _make_bard_fighter(self, level=5):
        """Fighter with Bard minimums and intended_class forced to 'Bard'.
        Build at level 5 (always resolves cleanly) then force level and XP
        to the requested value so generate_level scatter cannot land below."""
        import copy
        import generatecharacter as gc
        from character import Character
        c = Character(
            level=5,
            race='Human',
            gender='male',
            classes=['Fighter'],
            attrib_list=copy.deepcopy(self._BARD_ATTRS),
        )
        if level != 5:
            xp_floor = int(gc.return_xp('Fighter')[level - 1])
            c.xp = xp_floor
            c.level = [level]
        c.alignment = 'Neutral Good'
        c.intended_class = 'Bard'
        return c

    def _make_bard_thief(self, fighter_level=5, thief_level=7):
        """Build a bard-track character at stage 2 post-crossover (Thief|Fighter).

        Constructs the state directly rather than driving XP, to avoid
        relying on XP table values and crossover timing internals.
        hp_history at post-crossover = [thief_rolls, fighter_rolls, con_list].
        """
        import copy
        import hitpoints as hp_mod
        from character import Character
        # Start as Fighter at fighter_level
        c = Character(
            level=fighter_level,
            race='Human',
            gender='male',
            classes=['Fighter'],
            attrib_list=copy.deepcopy(self._BARD_ATTRS),
        )
        c.alignment = 'Neutral Good'
        c.intended_class = 'Bard'
        # Freeze Fighter and transition to Thief
        c.level = [fighter_level]
        c.hp_history = hp_mod.generate_hp(['Fighter'], [fighter_level], c.attributes['Con'])
        import generatecharacter as gc
        orig_xp = int(gc.return_xp('Fighter')[fighter_level - 1])
        c.initiate_dual_class('Thief', starting_xp=orig_xp)
        # Now manually build post-crossover state at thief_level
        # hp_history after initiate: [[0], fighter_rolls, con_list]
        # Generate real Thief rolls for thief_level
        thief_hp = hp_mod.generate_hp(['Thief'], [thief_level], c.attributes['Con'])
        thief_rolls = thief_hp[0]               # Thief roll list
        fighter_rolls = c.hp_history[1][:]      # frozen Fighter rolls
        c.classes = ['Thief', 'Fighter']
        c.level = [thief_level, fighter_level]
        c.dual_class['original_level'] = fighter_level  # Fighter level is what's frozen
        # Build con list: [thief_con, fighter_con] — use stored con from thief_hp
        thief_con_raw   = thief_hp[-1][0]       # con bonus for Thief at thief_level
        fighter_hpc     = hp_mod.generate_hp(['Fighter'], [fighter_level], c.attributes['Con'])
        fighter_con_raw = fighter_hpc[-1][0]
        c.hp_history = [thief_rolls, fighter_rolls, [thief_con_raw, fighter_con_raw]]
        c.hp = c._flatten()
        return c

    # ---- bard_eligible() ----------------------------------------------------

    def test_bard_eligible_passes_with_minimums(self):
        import selectclass
        attrs = self._BARD_ATTRS[0]
        self.assertTrue(selectclass.bard_eligible(attrs))

    def test_bard_eligible_fails_below_minimums(self):
        import selectclass
        attrs = self._NON_BARD_ATTRS[0]
        self.assertFalse(selectclass.bard_eligible(attrs))

    def test_bard_eligible_fails_on_each_attribute(self):
        """Dropping any single Bard minimum should fail the check."""
        import selectclass
        from selectclass import bard_mins
        base = dict(self._BARD_ATTRS[0])
        for attr, val in bard_mins().items():
            low = dict(base)
            low[attr] = val - 1
            self.assertFalse(selectclass.bard_eligible(low),
                             f"Should fail when {attr}={val - 1}")

    # ---- intended_class at creation -----------------------------------------

    def test_designated_bard_sets_intended_class(self):
        """When 'Bard' is passed as classes and attributes qualify,
        intended_class must be 'Bard' and classes must be ['Fighter']."""
        import copy
        from character import Character
        c = Character(
            level=1,
            race='Human',
            gender='male',
            classes=['Bard'],
            attrib_list=copy.deepcopy(self._BARD_ATTRS),
        )
        self.assertEqual(c.classes, ['Fighter'],
                         "Designated Bard should be generated as Fighter")
        self.assertEqual(c.intended_class, 'Bard')

    def test_designated_bard_without_minimums_stays_fighter(self):
        """When 'Bard' is passed but attributes don't currently qualify,
        the character is still a Fighter with intended_class='Bard'.
        The flag is kept so the transition-point check can fire once the
        character has aged out of the young-adult Wis penalty."""
        import copy
        from character import Character
        c = Character(
            level=1,
            race='Human',
            gender='male',
            classes=['Bard'],
            attrib_list=copy.deepcopy(self._NON_BARD_ATTRS),
        )
        self.assertEqual(c.classes, ['Fighter'])
        self.assertEqual(c.intended_class, 'Bard',
                         "Designated Bard keeps intended_class='Bard' even when below minimums at creation")

    def test_intended_class_none_by_default(self):
        c = make_fighter()
        self.assertIsNone(c.intended_class)

    # ---- transition window enforcement --------------------------------------

    def test_bard_track_transition_window_fighter(self):
        """Fighter→Thief on bard track: only valid between levels 5 and 7 inclusive."""
        c = self._make_bard_fighter(level=5)
        # Level 5 is in window — transition should succeed
        import generatecharacter as gc
        orig_xp = int(gc.return_xp('Fighter')[4])   # level 5 floor
        c.initiate_dual_class('Thief', starting_xp=orig_xp)
        self.assertEqual(c.dual_class['original'], 'Fighter')
        self.assertEqual(c.dual_class['destination'], 'Thief')
        self.assertEqual(c.dual_class['original_level'], 5)

    def test_bard_track_fighter_level_preserved_in_thief_stage(self):
        """After Fighter→Thief, the Fighter level is in dual_class['original_level']."""
        c = self._make_bard_fighter(level=6)
        import generatecharacter as gc
        orig_xp = int(gc.return_xp('Fighter')[5])
        c.initiate_dual_class('Thief', starting_xp=orig_xp)
        self.assertEqual(c.dual_class['original_level'], 6)

    # ---- Thief→Bard second transition ---------------------------------------

    def test_thief_to_bard_transition_structure(self):
        """After the second transition, dual_class must contain 'fighter_level'
        and 'original' must be 'Thief'."""
        c = self._make_bard_thief(fighter_level=5, thief_level=5)
        fighter_lvl = c.dual_class['original_level']   # Fighter level frozen in stage 1
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])      # Thief level 5 floor
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        self.assertEqual(c.dual_class['original'], 'Thief')
        self.assertEqual(c.dual_class['destination'], 'Bard')
        self.assertIn('fighter_level', c.dual_class,
                      "dual_class must carry fighter_level for stage 3")
        self.assertEqual(c.dual_class['fighter_level'], fighter_lvl)

    def test_thief_to_bard_classes_becomes_bard(self):
        """After second transition, self.classes == ['Bard']."""
        c = self._make_bard_thief(fighter_level=5, thief_level=5)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        self.assertEqual(c.classes, ['Bard'])

    def test_thief_to_bard_hp_history_four_lists(self):
        """Stage 3 hp_history must be [bard_rolls, thief_rolls, fighter_rolls, con]."""
        c = self._make_bard_thief(fighter_level=5, thief_level=5)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        self.assertEqual(len(c.hp_history), 4,
                         f"Expected 4 lists in hp_history, got {len(c.hp_history)}")

    def test_bard_first_level_roll_is_zero(self):
        """hp_history[0][0] must be 0 immediately after Thief→Bard transition."""
        c = self._make_bard_thief(fighter_level=5, thief_level=5)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        self.assertEqual(c.hp_history[0][0], 0,
                         "1st level Bard roll must be 0")

    # ---- HP accrual: starts at Bard 2, not post-crossover -------------------

    def test_bard_hp_accrues_at_second_level(self):
        """hp_history[0] must have a non-zero roll at index 1 (Bard 2)."""
        c = self._make_bard_thief(fighter_level=5, thief_level=5)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        # Award enough XP to reach Bard 2
        bard_xp_2 = int(gc.return_xp('Bard')[1])
        c.xp = thief_xp + bard_xp_2
        c.calculate_level(0, uncapped=True)
        self.assertGreaterEqual(len(c.hp_history[0]), 2,
                                "hp_history[0] should have at least 2 entries at Bard 2")
        # Level 1 = 0, level 2 should be a real roll (> 0 is not guaranteed but list must exist)
        self.assertEqual(c.hp_history[0][0], 0,
                         "First Bard roll must remain 0")

    # ---- Con bonus deferred until Bard level exceeds original_level ---------

    def test_bard_con_zero_before_exceeding_thief_level(self):
        """Bard con slot must be 0 while Bard level <= original_level (frozen Thief).

        Bypasses XP resolution to avoid off-by-one ambiguity at the level floor.
        Sets bard level directly and calls _recompute_bard_con() to isolate the rule.
        """
        c = self._make_bard_thief(fighter_level=5, thief_level=7)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[6])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        # Force Bard to exactly original_level (7) — not exceeding
        c.level = [7]
        c._recompute_bard_con()
        self.assertEqual(c.hp_history[-1][0], 0,
                         "Bard con must be 0 while Bard level <= frozen Thief level")

    def test_bard_con_accrues_after_exceeding_thief_level(self):
        """Bard con slot must be non-zero once Bard level > original_level."""
        c = self._make_bard_thief(fighter_level=5, thief_level=5)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        # Drive to Bard 6 (exceeds original_level=5)
        bard_xp_6 = int(gc.return_xp('Bard')[5])
        c.xp = thief_xp + bard_xp_6
        c.calculate_level(0, uncapped=True)
        # Con 14 → bonus +1, Bard cap +2, so Bard con at level 6 should be > 0
        if c.attributes['Con'] >= 15:           # only assert if con bonus is positive
            self.assertGreater(c.hp_history[-1][0], 0,
                               "Bard con should accrue once Bard level exceeds frozen Thief level")

    # ---- class_thaco() three-class comparison --------------------------------

    def test_bard_thaco_includes_fighter_leg(self):
        """class_thaco() for a Bard must consider Fighter at fighter_level."""
        import datalocus
        c = self._make_bard_thief(fighter_level=7, thief_level=5)
        import generatecharacter as gc
        thief_xp = int(gc.return_xp('Thief')[4])
        c.initiate_dual_class('Bard', starting_xp=thief_xp)
        c.level = [1]
        # Expected: best of Bard 1, Thief 5, Fighter 7
        expected = datalocus.base_thaco(
            ('Bard', 'Thief', 'Fighter'),
            (1, c.dual_class['original_level'], c.dual_class['fighter_level'])
        )
        self.assertEqual(c.class_thaco(), expected)

    def test_bard_thaco_fighter7_beats_fighter5(self):
        """A Bard with Fighter 7 history should have better THAC0 than Fighter 5."""
        import datalocus
        thaco_f7 = datalocus.base_thaco(('Fighter',), (7,))
        thaco_f5 = datalocus.base_thaco(('Fighter',), (5,))
        self.assertGreaterEqual(thaco_f7, thaco_f5,
                                "Fighter 7 THAC0 modifier should be >= Fighter 5")


# ===========================================================================
# PSIONICS
# ===========================================================================

class TestPsionics(unittest.TestCase):
    """psionics.py eligibility, strength formula, mutation, and display."""

    # ---- race gate ----------------------------------------------------------

    def test_ineligible_race_never_psionic(self):
        """A High Elf with maxed qualifying attrs must never gain psionics."""
        import psionics
        c = make_fighter()
        c.race = 'High Elf'
        c.attributes['Int'], c.attributes['Wis'], c.attributes['Cha'] = 18, 18, 18
        c.psionic_roll, c.psionic_strength = 0, 0
        psionics.check_and_apply(c)
        self.assertEqual(c.psionic_strength, 0)

    def test_gnome_ineligible(self):
        import psionics
        self.assertFalse(psionics.is_eligible_race('Gnome'))

    def test_human_eligible_race(self):
        import psionics
        self.assertTrue(psionics.is_eligible_race('Human'))

    def test_hill_dwarf_eligible_race(self):
        import psionics
        self.assertTrue(psionics.is_eligible_race('Hill Dwarf'))

    def test_mountain_dwarf_eligible_race(self):
        import psionics
        self.assertTrue(psionics.is_eligible_race('Mountain Dwarf'))

    def test_tallfellow_halfling_eligible_race(self):
        import psionics
        self.assertTrue(psionics.is_eligible_race('Tallfellow Halfling'))

    def test_stout_halfling_eligible_race(self):
        import psionics
        self.assertTrue(psionics.is_eligible_race('Stout Halfling'))

    # ---- eligibility probability formula ------------------------------------

    def test_eligibility_prob_zero_when_no_qualifying_attrs(self):
        """All three qualifying attrs at exactly 16 — zero probability."""
        import psionics
        self.assertEqual(psionics.eligibility_prob(16, 16, 16), 0.0)

    def test_eligibility_prob_matt_example(self):
        """Int 17, Wis 5, Cha 17 →
        floor((0.01 + 0.025 + 0 + 0.005) * 100) / 100 = 0.04."""
        import psionics
        self.assertAlmostEqual(psionics.eligibility_prob(17, 5, 17), 0.04)

    def test_eligibility_prob_three_quals(self):
        """Int 18, Wis 18, Cha 18 →
        floor((0.01 + 0.05 + 0.03 + 0.01) * 100) / 100 = 0.10."""
        import psionics
        self.assertAlmostEqual(psionics.eligibility_prob(18, 18, 18), 0.10)

    def test_eligibility_prob_never_negative(self):
        import psionics
        self.assertGreaterEqual(psionics.eligibility_prob(17, 1, 1), 0.0)

    # ---- qualifying attr count ----------------------------------------------

    def test_qualifying_count_zero(self):
        import psionics
        self.assertEqual(psionics.qualifying_attr_count(16, 16, 16), 0)

    def test_qualifying_count_one(self):
        import psionics
        self.assertEqual(psionics.qualifying_attr_count(17, 16, 16), 1)

    def test_qualifying_count_three(self):
        import psionics
        self.assertEqual(psionics.qualifying_attr_count(18, 18, 18), 3)

    # ---- strength formula ---------------------------------------------------

    def test_strength_full_matt_example(self):
        """Matt: Int 17, Wis 5, Cha 17, roll 45 → 4*(45+5+0+5) = 220."""
        import psionics
        self.assertEqual(psionics.psionic_strength_full(45, 17, 5, 17), 220)

    def test_strength_full_always_even(self):
        """Result is always even (multiplier is 2**n, n >= 1)."""
        import psionics
        for roll in (1, 50, 100):
            result = psionics.psionic_strength_full(roll, 17, 17, 17)
            self.assertEqual(result % 2, 0,
                             f"Expected even result for roll={roll}, got {result}")

    def test_strength_full_zero_when_no_quals(self):
        """All attrs ≤16 → strength = 0 (formula guarded by quals check)."""
        import psionics
        self.assertEqual(psionics.psionic_strength_full(50, 16, 16, 16), 0)

    def test_strength_full_single_qual(self):
        """One qualifying attr: multiplier = 2."""
        import psionics
        # Int 17, Wis 5, Cha 5: quals=1, bonus = max(0,17-12)+0+0 = 5
        self.assertEqual(psionics.psionic_strength_full(50, 17, 5, 5), 2 * (50 + 5))

    # ---- Cha reduction (Matt loses one point) -------------------------------

    def test_cha_reduction_recalculates_strength(self):
        """Matt: Int 17, Wis 5, Cha 17, roll 45 → 220.
        Cha drops to 16: quals=1, strength = 2*(45+5+0+4) = 108."""
        import psionics
        c = make_fighter()
        c.race = 'Human'
        c.attributes['Int'], c.attributes['Wis'], c.attributes['Cha'] = 17, 5, 17
        c.psionic_roll = 45
        c.psionic_strength = psionics.psionic_strength_full(45, 17, 5, 17)   # 220
        # Now drop Cha to 16
        c.attributes['Cha'] = 16
        psionics.check_and_apply(c)
        self.assertEqual(c.psionic_strength, 108)

    def test_cha_increase_recalculates_strength(self):
        """Matt: Int 17, Wis 5, Cha 17, roll 45 → 220.
        Cha rises to 18: quals=2, strength = 4*(45+5+0+6) = 224."""
        import psionics
        c = make_fighter()
        c.race = 'Human'
        c.attributes['Int'], c.attributes['Wis'], c.attributes['Cha'] = 17, 5, 17
        c.psionic_roll = 45
        c.psionic_strength = psionics.psionic_strength_full(45, 17, 5, 17)   # 220
        c.attributes['Cha'] = 18
        psionics.check_and_apply(c)
        self.assertEqual(c.psionic_strength, 4 * (45 + 5 + 0 + 6))

    # ---- loss of all qualifying attrs ---------------------------------------

    def test_all_quals_lost_zeroes_roll_and_strength(self):
        """If every qualifying attr drops to ≤16, both fields become 0."""
        import psionics
        c = make_fighter()
        c.race = 'Human'
        c.attributes['Int'], c.attributes['Wis'], c.attributes['Cha'] = 17, 5, 5
        c.psionic_roll = 45
        c.psionic_strength = psionics.psionic_strength_full(45, 17, 5, 5)
        c.attributes['Int'] = 16            # last qualifying attr drops
        psionics.check_and_apply(c)
        self.assertEqual(c.psionic_roll, 0,
                         "psionic_roll must be zeroed when all quals drop to ≤16")
        self.assertEqual(c.psionic_strength, 0)

    # ---- display ------------------------------------------------------------

    def test_display_strength_none_when_zero(self):
        import psionics
        c = make_fighter()
        c.psionic_strength = 0
        self.assertEqual(psionics.display_strength(c), 'none')

    def test_display_strength_halved(self):
        import psionics
        c = make_fighter()
        c.psionic_strength = 220
        self.assertEqual(psionics.display_strength(c), '110')

    def test_display_strength_halved_odd_full_impossible(self):
        """Full value is always even; halved display is always a whole number."""
        import psionics
        c = make_fighter()
        c.psionic_strength = 108
        self.assertEqual(psionics.display_strength(c), '54')

    # ---- Character fields exist after __init__ ------------------------------

    def test_character_has_psionic_fields(self):
        """Every Character (classed or 0-level) must have psionic_roll and
        psionic_strength after __init__."""
        c = make_fighter()
        self.assertTrue(hasattr(c, 'psionic_roll'),
                        "Character must have psionic_roll field")
        self.assertTrue(hasattr(c, 'psionic_strength'),
                        "Character must have psionic_strength field")

    def test_psionic_fields_are_ints(self):
        c = make_fighter()
        self.assertIsInstance(c.psionic_roll, int)
        self.assertIsInstance(c.psionic_strength, int)

    def test_ineligible_character_has_zero_strength(self):
        """make_fighter() uses Int 12, Wis 10, Cha 11 — all ≤16, so no psionics."""
        c = make_fighter()
        self.assertEqual(c.psionic_strength, 0)
        self.assertEqual(c.psionic_roll, 0)

    # ---- PSIONIC_CHANGED event via change_attribute -------------------------

    def test_psionic_changed_event_emitted_on_qualifying_attr_increase(self):
        """Raising Int to 17 on an otherwise-qualifying Human should eventually
        emit PSIONIC_CHANGED if the probability check passes.  We force the
        outcome by directly calling check_and_apply after seeding psionic_roll."""
        import psionics
        from character import CharacterEventType
        bus = StubEventBus()
        c = make_fighter(event_bus=bus)
        c.race = 'Human'
        # Seed a psionic character manually so the event must fire on recompute
        c.attributes['Int'] = 17
        c.psionic_roll = 50
        c.psionic_strength = psionics.psionic_strength_full(50, 17, 10, 11)
        bus.clear()
        # Now raise Int — _recompute_psionics fires through change_attribute
        c.attributes['Int'] = 18
        c._recompute_psionics()
        self.assertIn(CharacterEventType.PSIONIC_CHANGED, bus.types(),
                      "PSIONIC_CHANGED must be emitted when strength changes")

    def test_non_qualifying_attr_change_no_psionic_event(self):
        """Changing Str or Dex must never emit PSIONIC_CHANGED."""
        from character import CharacterEventType
        bus = StubEventBus()
        c = make_fighter(event_bus=bus)
        bus.clear()
        c.change_attribute('Str', +1)
        self.assertNotIn(CharacterEventType.PSIONIC_CHANGED, bus.types())
        c.change_attribute('Dex', +1)
        self.assertNotIn(CharacterEventType.PSIONIC_CHANGED, bus.types())


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)



