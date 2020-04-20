"""the main script. this is the start"""

from typing import List

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from uipit import UiPit
from ui_board import UIBoard
# todo:
# why is it crash on 3th turn =2
# add minimax algorithm =3->5
# playyyy testing a alotttt =

# return to original colors of buttons =2
# buttons colors =2
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
    def get_pits_from_object(pits_list: List[UiPit], object_parent) -> None:
        """
        save the pits of children of this widgets.
        :param pits_list: the list where we stone the list. (pointer)
        :param object_parent: the object we search
        :return: None
        """
        for widget in object_parent.children:
            if isinstance(widget, UiPit):
                pits_list.append(widget)
            else:
                PlayLayout.get_pits_from_object(pits_list, widget)

    def get_pits(self) -> List[UiPit]:
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
