from typing import List, Optional, Callable
from enum import Enum


class PartyEventType(Enum):                         # events emitted by Party operations
    MEMBER_ADDED, MEMBER_REMOVED, PARTY_REORDERED, PARTY_SORTED, PARTY_CLEARED = \
        "member_added", "member_removed", "party_reordered", "party_sorted", "party_cleared"


class Party:
    MAX_SIZE = 8

    def __init__(self, event_bus=None):             # initializes empty party; optional eventbus to emit domain events
        self.members: List = []
        self.event_bus = event_bus

    def add_member(self, character) -> bool:
        if len(self.members) >= self.MAX_SIZE:
            return False
        if character in self.members:
            return False
        self.members.append(character)              # adds a character to the party
        if self.event_bus:                          # emits the event
            self.event_bus.emit(PartyEventType.MEMBER_ADDED, {'character': character, 'name': character.character_name,
                                                              'party_size': len(self.members),
                                                              'position': len(self.members) - 1})
        return True

    def remove_member(self, character) -> bool:
        if character not in self.members:
            return False
        position = self.members.index(character)
        self.members.remove(character)              # removes a character from the party
        if self.event_bus:                          # emits the event
            self.event_bus.emit(PartyEventType.MEMBER_REMOVED, {'character': character,
                                                                'name': character.character_name,
                                                                'party_size': len(self.members),
                                                                'former_position': position})
        return True

    def move_member(self, character, new_position: int) -> bool:
        if character not in self.members:
            return False
        if new_position < 0 or new_position >= len(self.members):
            return False
        old_position = self.members.index(character)
        self.members.insert(new_position, self.members.pop(old_position))   # moves character to new position
        if self.event_bus:                          # emits the event
            self.event_bus.emit(PartyEventType.PARTY_REORDERED, {'character': character,
                                                                 'name': character.character_name,
                                                                 'old_position': old_position,
                                                                 'new_position': new_position})
        return True

    def sort_by(self, key_function: Callable, reverse: bool = False) -> None:
        old_order = self.members.copy()
        self.members.sort(key=key_function, reverse=reverse)
        if self.event_bus:
            self.event_bus.emit(PartyEventType.PARTY_SORTED, {'old_order': old_order, 'new_order': self.members.copy(),
                                                              'party_size': len(self.members)})

    def sort_by_combat_value(self) -> None:
        def calculate_combat_value(unit):
            ac = 10 + unit.calculate_ac()
            return unit.hp * (25 - ac) / 15
        self.sort_by(calculate_combat_value, reverse=True)

    def clear(self) -> None:
        old_members = self.members.copy()
        self.members = []                           # empties party
        if self.event_bus:
            self.event_bus.emit(PartyEventType.PARTY_CLEARED, {'former_members': old_members,
                                                               'count': len(old_members)})

    def get_member(self, index: int):
        if 0 <= index < len(self.members):          # get party member by position
            return self.members[index]
        return None

    def get_position(self, character) -> Optional[int]:
        try:
            return self.members.index(character)    # returns position of party member
        except ValueError:
            return None

    def contains(self, character) -> bool:
        return character in self.members            # checks whether character is in the party

    def is_full(self) -> bool:
        return len(self.members) >= self.MAX_SIZE   # checks whether party is full

    def is_empty(self) -> bool:
        return len(self.members) == 0               # checks whether party is empty

    def size(self) -> int:
        return len(self.members)                    # returns porty size

    def __len__(self) -> int:
        return len(self.members)

    def __iter__(self):
        return iter(self.members)

    def __contains__(self, character) -> bool:
        return character in self.members

    def __repr__(self) -> str:
        names = [m.character_name for m in self.members]
        return f"Party({len(self.members)} members: {names})"
