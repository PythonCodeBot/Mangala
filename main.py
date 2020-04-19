from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from typing import List

from data_types import *
from ai import AI
from link_list import LinkList
from pit import Pit
from ui_board import UIBoard
from defs import *
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
    pit_type: int = -1
    pass


class PitColumn(BoxLayout):
    pass


class PlayLayout(BoxLayout):
    # the game manager
    # move stones
    # end turns
    # and so

    @staticmethod
    def get_pits_from_object(pits_list: List[Pit], object_parent):
        for widget in object_parent.children:
            if isinstance(widget, Pit):
                pits_list.append(widget)
            else:
                PlayLayout.get_pits_from_object(pits_list, widget)

    def get_pits(self) -> List[Pit]:
        return_list = []
        PlayLayout.get_pits_from_object(return_list, self)
        return return_list


class MainLayout(BoxLayout):
    pits_layout: PlayLayout
    title_text: Label


class Mangala(App):
    game_layout: GridLayout
    turn_manager: UIBoard

    def build(self):
        self.game_layout = MainLayout()

        return self.game_layout

    def on_start(self):
        pits_list = self.game_layout.pits_layout.get_pits()

        self.turn_manager = UIBoard(pits_list, self.game_layout.title_text)

        for x in pits_list:
            x.init(self.turn_manager)


if __name__ == '__main__':
    Mangala().run()
