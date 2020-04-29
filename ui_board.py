"""this class connect the backend and the ui"""

from __future__ import annotations

from typing import List, Dict, Iterator
from copy import deepcopy
from threading import Thread, Lock

from kivy.uix.label import Label

import pit_board
from data_types import PitData, ImpactData, UiMethodsIndexes
import defs
import uipit
import ai

# todo fix the color when ai play
# todo fix the finish game


class UIBoard:
    """
    connect the UI to the logic
    get from the board instructions and exec them
    """

    board_data: pit_board.PitBoard  # the logic of the board. where the data of the pits are
    pits: List[uipit.UiPit]  # the ui pits
    title: Label  # the title of the game
    backup: pit_board.PitBoard  # is the old board before user confirm the move
    pit_to_index: Dict[uipit.UiPit, int]  # from data to index
    COLORS: List[List[int]] = [[0, 1, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1]]  # colors
    board_mutex: Lock  # mutex for preventing freeze
    ai_logic: ai.AI

    def __init__(self, pits: List[uipit.UiPit], title_text: Label) -> None:
        """
        init the class
        :param pits: the ui pits to change them from the
        :param title_text: the title of the game instructions
        """
        self.backup = None
        self.pit_to_index = {}
        self.pits = pits
        self.board_data = pit_board.PitBoard(pits)
        self.ai_logic = ai.AI(self)
        self.title = title_text
        self.board_mutex = Lock()

        self.ui_funcs = {
            UiMethodsIndexes.UPDATE_TEXT: self.update_pit,
            UiMethodsIndexes.ENABLE_PIT: self.enable_pit,
            UiMethodsIndexes.DISABLE_PIT: self.disable_pit,
            UiMethodsIndexes.CHANGE_TITLE: self.update_title,
            UiMethodsIndexes.TAKE_OPPONENT_STONES: self.steal_stones,
            UiMethodsIndexes.ANOTHER_TURN: self.another_turn
        }

        instructions = self.board_data.set_turn()
        # make move by reading data impact
        self.call_instructions(instructions)

        node = self.board_data.pits_link_list.start
        for index, pit in enumerate(pits):
            self.pit_to_index[pit] = index

            stones = defs.START_STONES_PER_PIT
            if index == 0 or index == len(pits) - 1:
                stones = defs.START_STONES_PER_JACKPOT

            pit.update_text(stones)
            node = node.right_node

        # if ai start
        if self.board_data.now_turn:
            self.play_ai()

    def call_ui_func(self, return_data: ImpactData) -> None:
        """
        get the func and call it
        :param return_data: the arg for the func
        :return: None
        """
        self.ui_funcs[return_data.impact_index](return_data.arg)

    def update_pit(self, pit: PitData) -> None:
        """
        update the stones value
        :return: None
        """

        ui_pit = self.get_ui_pit(pit)

        ui_pit.update_text(self.board_data.pits_list[pit.index].stones)

    def update_title(self, new_text: str) -> None:
        """
        change the title
        :param new_text: the new title
        :return: None
        """
        self.title.text = new_text

    def get_ui_pit(self, pit: PitData) -> uipit.UiPit:
        """
        from data to ui pit
        :param pit: the data of the pit
        :return: ui pit
        """
        return self.pits[pit.index]

    def enable_pit(self, pit: PitData) -> None:
        """
        make the pit clickable
        :param pit: the data if the pit
        :return: None
        """
        self.do_enable_pit(pit, True)

    def disable_pit(self, pit: PitData) -> None:
        """
        make the pit not clickable
        :param pit: the data if the pit
        :return: None
        """
        self.do_enable_pit(pit, False)

    def update_color(self, pit: PitData, color_id: int) -> None:
        """
        change the color of the pit
        :param pit: the wonted pit
        :param color_id: id of the color
        :return: None
        """
        pit = self.get_ui_pit(pit)
        pit.background_color = self.COLORS[color_id]

    def another_turn(self, pit: PitData) -> None:
        """
        if the next the player will have another turn
        :param pit: the pit that change the color
        :return: None
        """
        self.update_color(pit, 0)

    def steal_stones(self, pit: PitData) -> None:
        """
        if the next the player will take the stones of the enemy
        :param pit: the pit that change the color
        :return: None
        """
        self.update_color(pit, 1)

    def do_enable_pit(self, pit: PitData, enable: bool) -> None:
        """
        enable or disabled pit
        :param pit: the pit we wont to change
        :param enable: enable or disabled
        :return: None
        """
        ui_pit = self.get_ui_pit(pit)
        ui_pit.disabled = not enable

    def call_instructions(self, instructions: Iterator[ImpactData]) -> None:
        """
        call the funcs of the instructions
        :param instructions: the instructions
        :return: None
        """
        for instruction in instructions:
            self.call_ui_func(instruction)

    def show_move_thread(self, played_pit: uipit.UiPit) -> None:
        """
        show the next move. just make the turn but save the before if user not clicked
        :param played_pit: the button that user over
        :return: None
        """

        # stop or wait for the next show.
        # prevent show two times at once
        self.board_mutex.acquire()

        # save before
        self.backup = deepcopy(self.board_data)
        instructions = self.board_data.make_move(self.pit_to_index[played_pit])

        # make move by reading data impact
        self.call_instructions(instructions)

    def show_move(self, played_pit: uipit.UiPit) -> None:
        """
        show the move. without making it
        this func are called when the user hover over the button.
        :param played_pit: which button call it
        :return:
        """

        thread = Thread(target=self.show_move_thread, args=(played_pit,))
        thread.start()

    def update_text_of_pits(self) -> None:
        """
        update the number of pits in all pits
        :return: None
        """
        for pit in self.board_data.pits_list:
            self.update_pit(pit)

    def cancel_move(self) -> None:
        """
        if user not click the button
        this func are called when the user stop hovering over the button.
        :return: None
        """

        # get backup
        self.board_data = self.backup

        self.update_text_of_pits()

        # make move by reading data impact
        self.pits_default_colors()

        # wait for the next hover
        self.board_mutex.release()

    def play_ai(self):
        print("ai turn!")
        board = self.board_data
        ai_play_index = self.ai_logic.play()
        print(ai_play_index)
        if ai_play_index != -1:
            instructions = board.make_move(ai_play_index)
            self.call_instructions(instructions)
            self.call_instructions(self.board_data.set_turn())
            self.pits_default_colors()
            print("who turn is it:", self.board_data.now_turn)
        else:
            print("cant play")

    def confirm_move(self) -> None:
        """
        if user not click the button
        this func are called when the user click button.
        :return: None
        """

        self.board_mutex.release()
        # delete backup and buttons
        self.backup = None

        self.pits_default_colors()
        self.call_instructions(self.board_data.set_turn())
        while self.board_data.now_turn and not self.board_data.have_win():
            self.play_ai()

    def pits_default_colors(self) -> None:
        """
        make all the pits default color
        :return: None
        """
        for pit in self.pits:
            pit.background_color = self.COLORS[2]
