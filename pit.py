"""pit is uses as button and visual"""
from typing import List
from threading import Thread, Lock

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

from hoverable import HoverBehavior
from data_types import PlayRecode
from defs import START_STONES_PER_JACKPOT, START_STONES_PER_PIT


class Pit(Button, HoverBehavior):
    """
    pit of the player, can be jackpot. update the TurnManager.
    """
    default_background_color: List[int] = Button.background_color
    stones_text: Label = ObjectProperty(None, allownone=True)  # the text on the stone
    pit_type: int = -1  # 0, 1 for users jackpot. 2, 3 for regular pits
    manager = None  # fixme the name and the typing
    return_recode: PlayRecode = PlayRecode()  # object with the last play data
    pressed = False  # if has been press
    can_be_pressed = False  # if can be press
    mutex: Lock  # the mutex for the data
    thread: Thread  # the new thread of show data

    def init(self, manager) -> None:
        """
        init the class. cant be __init__ because the kv file
        :param manager: the turn manager
        :param mutex: the mutex of the data
        :return: None
        """

        # check if it jackpot
        #self.stones = START_STONES_PER_JACKPOT if self.pit_type < 2 else START_STONES_PER_PIT
        #self.update_text(4)
        self.manager = manager

    def set_stones(self, stones: int) -> None:
        """
        set new pit stones
        :param stones: the new stones
        :return: None
        """
        self.pit_manager.stones = stones
        self.update_text()

    def add_stone(self) -> None:
        """
        inc stones by one
        :return: None
        """
        self.pit_manager.stones += 1

    def is_empty(self) -> bool:
        """
        if this pit is empty
        :return: is have zero stone
        """
        return self.stones == 0

    def on_press(self) -> None:
        """
        When the player press the pit. alert the turnManager
        :return: None
        """
        self.print("press", hex(id(self)))
        self.manager.confirm_move()
        self.can_be_pressed = False
        self.on_enter()

    def on_enter(self) -> None:
        """
        when player over the pit. alert the turnManager
        :return: None
        """
        if not self.disabled:
            self.can_be_pressed = True
            self.print("enter", hex(id(self)))
            # Thread for making the keep running and not freezing, prevent 'dead lock'
            self.manager.show_move(self)
            # self.thread = Thread(target=self.manager.show_move, args=(self, self.return_recode))
            # self.thread.start()

    def on_leave(self) -> None:
        """
        when player leave over the pit. alert the turnManager
        :return: None
        """
        if not self.disabled and self.can_be_pressed:
            self.print("leave", hex(id(self)), self.pressed)
            self.manager.cancel_move()
            self.pressed = False

    def update_text(self, text) -> None:
        """
        update the new stones value
        :return: None
        """
        self.stones_text.text = str(text)
