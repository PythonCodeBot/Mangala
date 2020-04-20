""" classes without very much logic, mainly data"""

from __future__ import annotations

from typing import List, Any
from dataclasses import dataclass

from defs import JACKPOT_TYPES_CODES,\
    PIT_TYPES_CODES, START_STONES_PER_PIT, START_STONES_PER_JACKPOT
from math import pi

class UiMethodsIndexes:
    """ui methods indexes for """

    UPDATE_TEXT = 0
    ENABLE_PIT = 1
    DISABLE_PIT = 2
    CHANGE_TITLE = 3
    ANOTHER_TURN = 4
    TAKE_OPPONENT_STONES = 5


class PitData:
    """ where the data of the pits stone. the logic part of the pits"""

    stones: int = -1  # stones
    pit_type: int = -1  # 0, 1 for users jackpot. 2, 3 for regular pits
    index: int = -1  # index of the pit in list

    def __init__(self, player_index: int, pit_index: int) -> None:
        """
        init the pit
        :param player_index: which player
        :param pit_index: index in pits list
        """
        self.pit_type = PIT_TYPES_CODES[player_index]
        self.stones = START_STONES_PER_PIT
        self.index = pit_index

    @classmethod
    def jackpot(cls, player_index: int, pit_index: int) -> PitData:
        """
        make jackpot data from index
        :param player_index: which player
        :param pit_index: index in pits list
        :return: the new class
        """
        return_class = cls(player_index, pit_index)
        return_class.stones = START_STONES_PER_JACKPOT
        return_class.pit_type = JACKPOT_TYPES_CODES[player_index]
        return return_class

    def is_empty(self) -> bool:
        """
        return if the pits is empty
        :return: if empty
        """
        return self.stones == 0


class ImpactData:
    """
    this class sent to the ui logic for
    separate backend from ui
    """

    impact_index: int  # which type of action make sound change color and so on
    arg: Any  # arg for the ui func. example: which pit is making the impact.

    def __init__(self, impact_index: int, arg: Any) -> None:
        """
        init the class
        :param impact_index: which imact
        :param arg: the arg for the ui func
        """
        self.arg = arg
        self.impact_index = impact_index

    @classmethod
    def update_text(cls, pit: PitData) -> ImpactData:
        """
        update text ui func
        :param pit: which pit update the text
        :return: new class
        """
        return cls(UiMethodsIndexes.UPDATE_TEXT, pit)

    @classmethod
    def enable_pit(cls, pit: PitData) -> ImpactData:
        """
        enable pit ui func
        :param pit: which pit enable
        :return: new class
        """
        return cls(UiMethodsIndexes.ENABLE_PIT, pit)

    @classmethod
    def disable_pit(cls, pit: PitData) -> ImpactData:
        """
        disable pit ui func
        :param pit: which pit disable
        :return: new class
        """
        return cls(UiMethodsIndexes.DISABLE_PIT, pit)

    @classmethod
    def change_title(cls, text: str) -> ImpactData:
        """
        change title text
        :param text: the new text
        :return: the class
        """
        return cls(UiMethodsIndexes.CHANGE_TITLE, text)

    @classmethod
    def another_turn(cls, pit: PitData) -> ImpactData:
        """
        ui func action if user have another turn
        :param pit: the pit the user play
        :return: new class
        """
        return cls(UiMethodsIndexes.ANOTHER_TURN, pit)

    @classmethod
    def take_opponent_stones(cls, pit: PitData) -> ImpactData:
        """
        ui func action if user take opponent stones
        :param pit: the parallel pit
        :return: new class
        """
        return cls(UiMethodsIndexes.TAKE_OPPONENT_STONES, pit)


@dataclass
class Player:
    """
    player data
    """

    jackpot: PitData  # the jackpot of the player
    pits: List[PitData]  # P1 : lefter the zeroes. [0] top right button, [5] top left button
    # [0] top right up, [5] top left up
    user_id: int

    def __init__(self, user_id: int, all_pits: List[PitData]) -> None:
        """
        init the class
        :param user_id: player one or two
        :param all_pits: list of all the pits
        """
        self.user_id = user_id

        pits_size = len(all_pits)
        half_size = pits_size // 2

        # or last or first
        self.jackpot = all_pits[user_id * -1]

        if user_id:
            self.pits = all_pits[1:half_size]
        else:
            self.pits = all_pits[half_size:-1]
