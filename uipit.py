"""pit is uses as button and visual"""

from __future__ import annotations

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

from hoverable import HoverBehavior
import ui_board


class UiPit(Button, HoverBehavior):
    """
    pit of the player, can be jackpot.
    this is the input from the player. (and output)
    update the TurnManager.
    """

    stones_text: Label = ObjectProperty(None, allownone=True)  # the text on the stone
    pit_type: int = -1  # 0, 1 for users jackpot. 2, 3 for regular pits
    manager: ui_board.UIBoard  # UI class. use for give the ui the input
    pressed = False  # if has been press
    can_be_pressed = False  # if can be press

    def init(self, manager: ui_board.UIBoard) -> None:
        """
        init the class. cant be __init__ because of kv file
        :param manager: the ui turn manager
        :return: None
        """
        self.manager = manager

    def on_press(self) -> None:
        """
        When the player press the pit. alert the turnManager. confirm the move
        :return: None
        """
        self.print("press", hex(id(self)))
        self.manager.confirm_move()
        self.can_be_pressed = False
        self.on_enter()

    def on_enter(self) -> None:
        """
        when player over the pit. alert the turnManager show the move
        :return: None
        """
        if not self.disabled:
            self.can_be_pressed = True
            # Thread for making the keep running and not freezing, prevent 'dead lock'
            self.manager.show_move(self)

    def on_leave(self) -> None:
        """
        when player leave over the pit. alert the turnManager
        :return: None
        """
        if not self.disabled and self.can_be_pressed:
            self.manager.cancel_move()
            self.pressed = False

    def update_text(self, text) -> None:
        """
        update the new stones value
        :return: None
        """
        self.stones_text.text = str(text)
