from __future__ import annotations

from typing import List, Any

from link_list import Node
from defs import JACKPOT_TYPES_CODES, PIT_TYPES_CODES , START_STONES_PER_PIT, START_STONES_PER_JACKPOT


class UiMethodsDefine:
    UPDATE_TEXT_INDEX = 0
    ENABLE_PIT_INDEX = 1
    DISABLE_PIT_INDEX = 2
    CHANGE_TITLE_INDEX = 3
    ANOTHER_TURN_INDEX = 4
    TAKE_OPPONENT_STONES_INDEX = 5



class PlayRecode:
    original_pit_node: Node
    original_stones: int
    parallel_orig_stones: int = 0
    another_turn: bool


class PitData:
    stones: int = -1  # stones
    pit_type: int = -1  # 0, 1 for users jackpot. 2, 3 for regular pits
    index: int = -1

    def __init__(self, player_index: int, pit_index: int) -> None:
        """
        init the pit
        :param player_index: which player
        """
        self.pit_type = PIT_TYPES_CODES[player_index]
        self.stones = START_STONES_PER_PIT
        self.index = pit_index

    @classmethod
    def jackpot(cls, player_index: int, pit_index: int) -> PitData:
        """
        make jackpot data from index
        :param player_index: which player
        :return: the new class
        """
        return_class = cls(player_index, pit_index)
        return_class.stones = START_STONES_PER_JACKPOT
        return_class.pit_type = JACKPOT_TYPES_CODES[player_index]
        return return_class

    def is_empty(self) -> bool:
        return self.stones == 0


class ImpactData:
    impact_index: int  # make sound change color and so on
    arg: Any  # example: which pit is making the impact.

    def __init__(self, impact_index: int, arg: Any) -> None:
        self.arg = arg
        self.impact_index = impact_index

    @classmethod
    def update_text(cls, pit: PitData) -> ImpactData:
        return cls(UiMethodsDefine.UPDATE_TEXT_INDEX, pit)

    @classmethod
    def enable_pit(cls, pit: PitData) -> ImpactData:
        return cls(UiMethodsDefine.ENABLE_PIT_INDEX, pit)

    @classmethod
    def disable_pit(cls, pit: PitData) -> ImpactData:
        return cls(UiMethodsDefine.DISABLE_PIT_INDEX, pit)

    @classmethod
    def change_title(cls, text: str) -> ImpactData:
        return cls(UiMethodsDefine.CHANGE_TITLE_INDEX, text)

    @classmethod
    def another_turn(cls, pit: PitData) -> ImpactData:
        return cls(UiMethodsDefine.ANOTHER_TURN_INDEX, pit)

    @classmethod
    def take_opponent_stones(cls, pit: PitData) -> ImpactData:
        return cls(UiMethodsDefine.TAKE_OPPONENT_STONES_INDEX, pit)


class Player:
    jackpot: PitData
    pits: List[PitData]  # P1 : lefter the zeroes. [0] top right button, [5] top left button
                     # [0] top right up, [5] top left up
    id: int

    def __init__(self, id: int, all_pits: List[PitData]):
        self.id = id

        pits_size = len(all_pits)
        half_size = pits_size // 2

        # or last or first
        self.jackpot = all_pits[id * -1]

        if id:
            self.pits = all_pits[1:half_size]
        else:
            self.pits = all_pits[half_size:-1]
