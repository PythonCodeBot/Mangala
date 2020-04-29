"""the main script. this is the start"""

from typing import List

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import uipit
from ui_board import UIBoard
# todo:

# return to original colors of buttons =2
# make layouts better looking =6
# add colors =6
# animation
# sound =7

# after hag refactor the hell of the code

# todo fucking never:
# real graphics = 8->10
# d3 title = 11
# NN AI = 12->?
# online
# music?!


class PitRaw(BoxLayout):
    """just a rwa of pits"""
    pit_type: int = -1


class PitColumn(BoxLayout):
    """just a column of pits"""


class PlayLayout(BoxLayout):
    """where the user can interact with the game"""

    @staticmethod
    def get_pits_from_object(pits_list: List[uipit.UiPit], object_parent) -> None:
        """
        save the pits of children of this widgets.
        :param pits_list: the list where we stone the list. (pointer)
        :param object_parent: the object we search
        :return: None
        """
        for widget in object_parent.children:
            if isinstance(widget, uipit.UiPit):
                pits_list.append(widget)
            else:
                PlayLayout.get_pits_from_object(pits_list, widget)

    def get_pits(self) -> List[uipit.UiPit]:
        """
        get all the pits in list
        :return: the list of pits
        """
        return_list = []
        PlayLayout.get_pits_from_object(return_list, self)
        return return_list


class MainLayout(BoxLayout):
    """the app lock"""
    pits_layout: PlayLayout
    title_text: Label


class Mangala(App):
    """start point of the app"""
    game_layout: GridLayout
    turn_manager: UIBoard

    def build(self) -> MainLayout:
        """
        build the app. kivy func
        :return: what we wont to build
        """
        self.game_layout = MainLayout()

        return self.game_layout

    def on_start(self) -> None:
        """
        init the classes and pit
        :return: None
        """
        pits_list = self.game_layout.pits_layout.get_pits()

        self.turn_manager = UIBoard(pits_list, self.game_layout.title_text)

        for pit in pits_list:
            pit.init(self.turn_manager)


if __name__ == '__main__':
    Mangala().run()
