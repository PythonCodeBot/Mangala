from typing import List, Dict
from copy import deepcopy

from kivy.uix.label import Label

from pit_board import PitBoard
import data_types
from data_types import PitData, Node, ImpactData, UiMethodsDefine
from pit import Pit
from threading import Thread, Lock

class UIBoard:
    """connect the UI to the logic"""

    board_data: PitBoard
    pits: List[Pit]
    title: Label
    backup: PitBoard  # is the old board before user confirm the move
    pit_to_index: Dict[Pit, int]
    data_to_pit: Dict[PitData, Pit]
    # R G B
    COLORS: List[List[int]] = [[0, 1, 0], [1, 1, 0]]
    board_mutex: Lock

    def __init__(self, pits: List[Pit], title_text: Label):
        self.backup = None
        self.pit_to_index = {}
        self.node_to_pit = {}
        self.data_to_pit = {}
        self.pits = pits
        self.board_data = PitBoard(pits)
        self.title = title_text
        self.board_mutex = Lock()

        self.ui_funcs = {UiMethodsDefine.UPDATE_TEXT_INDEX: self.update_pit,
                    UiMethodsDefine.ENABLE_PIT_INDEX: self.enable_pit,
                    UiMethodsDefine.DISABLE_PIT_INDEX: self.disable_pit,
                    UiMethodsDefine.CHANGE_TITLE_INDEX: self.update_title,
                    UiMethodsDefine.TAKE_OPPONENT_STONES_INDEX: self.steal_stones,
                    UiMethodsDefine.ANOTHER_TURN_INDEX: self.another_turn}

        node = self.board_data.pits_link_list.start
        for index, pit in enumerate(pits):
            self.pit_to_index[pit] = index
            self.data_to_pit[node.data] = pit
            pit.update_text(node.data.stones)
            node = node.right_node

        instructions = self.board_data.set_turn(True)
        # make move by reading data impact
        self.call_instructions(instructions)
        from time import sleep

        #pits[13].disabled = False

    def call_ui_func(self, return_data: ImpactData):
        print(self.ui_funcs[return_data.impact_index].__name__)
        self.ui_funcs[return_data.impact_index](return_data.arg)

    def update_pit(self, pit: PitData):
        """
        update the stones
        :return: None
        """

        ui_pit = self.get_ui_pit(pit)

        ui_pit.update_text(self.board_data.pits_list[pit.index].stones)

    def update_title(self, new_text: str):
        self.title.text = new_text

    def get_ui_pit(self, pit: PitData) -> Pit:
        return self.pits[pit.index]

    def enable_pit(self, pit: PitData):
        self.do_enable_pit(pit, True)

    def disable_pit(self, pit: PitData):
        self.do_enable_pit(pit, False)

    def update_color(self, pit: PitData, color_id: int):
        pit = self.get_ui_pit(pit)
        pit.background_color = self.COLORS[color_id]

    def another_turn(self, pit: PitData):
        self.update_color(pit, 0)

    def steal_stones(self, pit: PitData):
        self.update_color(pit, 1)

    def do_enable_pit(self, pit: PitData, enable: bool):
        ui_pit = self.get_ui_pit(pit)
        ui_pit.disabled = not enable

    def call_instructions(self, instructions):
        for instruction in instructions:
            self.call_ui_func(instruction)

    def show_move_thread(self, played_pit: Pit):
        # save backup
        self.board_mutex.acquire()
        # self.thread.start()
        self.backup = deepcopy(self.board_data)

        instructions = self.board_data.make_move(self.pit_to_index[played_pit])

        # make move by reading data impact
        self.call_instructions(instructions)

    def show_move(self, played_pit: Pit):
        """when user over"""
        self.thread = Thread(target=self.show_move_thread, args=(played_pit,))
        self.thread.start()


        # self.thread.start()

    def update_text_of_pits(self):
        for pit in self.board_data.pits_list:
            self.update_pit(pit)

    def cancel_move(self):
        """when user leave"""


        # get backup
        self.board_data = self.backup

        self.update_text_of_pits()

        # make move by reading data impact
        #self.call_instructions(instructions)

        self.board_mutex.release()
        # update he change buttons

    def confirm_move(self):
        """when user press"""
        self.board_mutex.release()
        # delete backup and buttons
        self.backup = None

        #self.board_data.set_turn(self.board_data.now_turn)
        old_turn = self.board_data.now_turn
        self.call_instructions(self.board_data.pit_buttons_disabled(self.board_data.now_turn))
