"""backend of the logic of the game"""

from __future__ import annotations

from typing import List, Iterator, Dict

from data_types import Player, PitData, ImpactData
from link_list import LinkList
from link_list import Node
import uipit


class PitBoard:
    """
    logic of the game, turn, and move stones
    """
    now_turn = False  # who turn is it
    player_one: Player  # player one data
    player_two: Player  # player two data
    pits_list: List[PitData]  # list of all the pits, include jackpots
    pits_link_list: LinkList[PitData]  # link list of the pits
    pits_to_node: Dict[PitData, Node[PitData]]  # fast way to get the node from pit
    last_play: bool  # the who play the last turn

    def __init__(self, pits: List[uipit.UiPit]) -> None:
        """
        init the TurnManager and the pits
        :param pits: list of pits first is player one jackpot. last is player two jackpot
        """

        self.pits_list = []
        self.pits_to_node = {}
        self.pits_list.append(PitData.jackpot(0, 0))
        self.size_of_pits = len(pits)

        half_size_pits = self.size_of_pits//2

        # feel the non jackpot pits
        for index in range(1, self.size_of_pits - 1):
            player_index = int(index > half_size_pits)
            self.pits_list.append(PitData(player_index, index))

        self.pits_list.append(PitData.jackpot(1, self.size_of_pits - 1))

        self.player_one = Player(0, self.pits_list)
        self.player_two = Player(1, self.pits_list)

        # init the players data

        # start of the link list is the player one jackpot
        self.pits_link_list = LinkList(self.player_one.jackpot)

        players_pits = zip(self.player_one.pits, self.player_two.pits)

        self.pits_to_node[self.player_one.jackpot] = self.pits_link_list.start
        # store the like list

        for index, (player_one_pit, player_two_pit) in enumerate(players_pits):
            # update codes

            most_right = self.pits_link_list.push_right(player_one_pit)
            most_left = self.pits_link_list.push_left(player_two_pit)

            # this is the parallel pit
            most_left.parallel_node = most_right
            most_right.parallel_node = most_left

            self.pits_to_node[player_one_pit] = most_right
            self.pits_to_node[player_two_pit] = most_left

        self.pits_link_list.push_right(self.player_two.jackpot)
        self.pits_link_list.make_looped()
        self.pits_to_node[self.player_two.jackpot] = self.pits_link_list.most_right

    def have_stones(self, player: bool) -> bool:
        """
        if the player have any stones in his pits
        :param player: which player
        :return: if have any stones
        """
        player = self.get_player(player)

        for pit in player.pits:
            if not pit.is_empty():
                return True
        return False

    def have_win(self) -> bool:
        """
        check if somebody win
        :return: if somebody win
        """
        return not self.have_stones(True) or not self.have_stones(False)

    def set_turn(self) -> Iterator[ImpactData]:
        """
        change the turn and check if someone is win
        :return: the actions the ui need to do
        """
        now_turn = self.now_turn

        assert sum([pit.stones for pit in self.pits_list]) == 48, "Stone Missing or adding stones in board"

        for instruction in self.pit_buttons_disabled(now_turn):
            yield instruction

        # if somebody don't have stones
        if self.have_win():
            print("END GAME")
            last_played_player = self.get_player(self.last_play)
            for pit in self.pits_list[1:-1]:
                last_played_player.jackpot.stones += pit.stones
                pit.stones = 0

            # last_played_player.jackpot.update_text()
            # todo fix color

            player_one_stones = self.get_player(False).jackpot.stones
            player_two_stones = self.get_player(True).jackpot.stones

            if player_one_stones != player_two_stones:

                new_title = "YOU" if player_one_stones < player_two_stones else "AI"
                new_title += " WIN!"
                yield ImpactData.change_title(new_title)
            else:
                new_title = "TIE!"
                yield ImpactData.change_title(new_title)

            enable_pits = self.disabled_player_pits(now_turn, False)
            disable_pits = self.disabled_player_pits(not now_turn, not False)

            # update text of the pits
            for pit in self.pits_list:
                yield ImpactData.update_text(pit)

            # disable all the pits
            for disable_pit in self.connect_generator(enable_pits, disable_pits):
                yield disable_pit

    @staticmethod
    def connect_generator(*generators) -> Iterator:
        """
        get generators and return one generator
        :param generators: the generators we wont to mash together
        :return: Iterator of all the enter generators
        """
        for generator in generators:
            for value in generator:
                yield value

    def pit_buttons_disabled(self, now_turn: bool) -> Iterator[ImpactData]:
        """
        enable of disable the buttons by user turn
        :param now_turn: which turn
        :return: the actions the ui need to do
        """
        enables_pits = self.disabled_player_pits(now_turn, False)
        disable_pits = self.disabled_player_pits(not now_turn, not False)

        return self.connect_generator(enables_pits, disable_pits)

    def disabled_player_pits(self, player: bool, disable: bool) -> Iterator[ImpactData]:
        """
        disabled or enable player pits buttons
        :param player: which player
        :param disable: disable or enable
        :return: the actions the ui need to do
        """
        wonted_player = self.get_player(player)
        yield ImpactData.disable_pit(wonted_player.jackpot)

        for pit in wonted_player.pits:
            if disable or pit.stones == 0:
                yield ImpactData.disable_pit(pit)
            else:
                yield ImpactData.enable_pit(pit)

    @staticmethod
    def get_next(pit_node: Node[PitData]) -> Node[PitData]:
        """
        get the next pit node
        :param pit_node: the start
        :return: the next pit
        """
        return pit_node.right_node

    def get_player(self, player: bool) -> Player:
        """
        get the player
        :param player: which player
        :return: the player class
        """
        return self.player_one if player else self.player_two

    def first_stones_logic(self, start_node: Node[PitData]) \
            -> Iterator[ImpactData]:
        """
        move first stones until he get to the last stone
        :param start_node: which pit the user move
        :return: the actions the ui need to do
        """
        other_player = self.get_player(self.now_turn)

        next_pit_node = self.get_next(start_node)
        start_pit = start_node.data
        while start_pit.stones > 1:
            next_pit = next_pit_node.data

            # skip other_player jackpot
            if next_pit is not other_player.jackpot:
                next_pit.stones += 1
                yield ImpactData.update_text(next_pit)
                start_pit.stones -= 1
            next_pit_node = self.get_next(next_pit_node)

        # delete last stone
        start_pit.stones -= 1
        yield ImpactData.update_text(start_pit)

        # when getting to the end
        return next_pit_node

    def can_take_stones(self, pit: Node[PitData]) -> bool:
        """
        if the user can take the parallel pits
        :param pit: the pit he check
        :return: if can or not
        """
        return pit.data in self.get_player(self.now_turn).pits \
            and pit.data.is_empty()

    def last_stone_logic(self, start_pit: Node[PitData], last_node: Node[PitData]) \
            -> Iterator[ImpactData]:
        """
        make the last stone logic
        :param start_pit: which pit the user moved
        :param last_node: where the move get, where to make the last stone logic
        for example: if the last stone land on empty player pit and so one
        :return: the actions the ui need to do
        """

        my_player = self.get_player(not self.now_turn)

        if last_node.data is self.get_player(self.now_turn).jackpot:
            last_node = self.get_next(last_node)

        next_pit = last_node
        next_turn = not self.now_turn

        # if have another turn
        if next_pit.data is my_player.jackpot:
            next_turn = self.now_turn

            yield ImpactData.another_turn(start_pit.data)

        if self.can_take_stones(next_pit):
            # take parallel pit stones to player jackpot

            parallel_pit = last_node.parallel_node.data

            yield ImpactData.take_opponent_stones(parallel_pit)

            my_player.jackpot.stones += parallel_pit.stones
            my_player.jackpot.stones += 1  # take also the stone that land on the empty pit
            parallel_pit.stones = 0

            yield ImpactData.update_text(parallel_pit)

            yield ImpactData.update_text(my_player.jackpot)
        else:
            next_pit.data.stones += 1

        yield ImpactData.update_text(next_pit.data)

        self.now_turn = next_turn

    def make_move(self, pit_index: int) -> Iterator[ImpactData]:
        """
        just move
        :param pit_index: which pit as index
        :return: the actions the ui need to do
        """
        self.last_play = not self.now_turn
        moved_pit = self.pits_list[pit_index]
        moved_pit_node = self.pits_to_node[moved_pit]

        first_stones = self.first_stones_logic(moved_pit_node)

        while True:

            try:
                yield next(first_stones)
            except StopIteration as return_next_pit:
                # getting the last pit of the turn
                for instruction in self.last_stone_logic(moved_pit_node, return_next_pit.value):
                    yield instruction
                break
