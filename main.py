import kivy
from typing import List
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.properties import ConfigParserProperty

from hoverable import HoverBehavior
from dataclasses import dataclass
from threading import Thread, Lock

# todo:
# show system instead of the old click to update +
# deUpdate func +
# fix the mutex bug +
# finish system =1
# git push =2
# add minimax algorithm =3->5
# sleep

# return to original colors of buttons =2
# buttons colors =2
# make layouts better looking =6
# add colors =6
# sound =7

# after hag refactor the hell of the code

# todo fucking never:
# real graphics = 8->10
# d3 title = 11
# NN AI = 12->?
# online
# music?!


START_STONES_PER_PIT = 4
START_STONES_PER_JACKPOT = 0

JACKPOT_TYPES_CODES = (0, 1)
PIT_TYPES_CODES = (2, 3)

class Node:
    def __init__(self, data_val=None):
        self.data = data_val
        self.right = None
        self.left = None
        self.parallel = None

    def insert_right(self, data_val):
        self.right = Node(data_val)
        return self.right

    def insert_left(self, data_val):
        self.left = Node(data_val)
        return self.left

class LinkList:
    #todo fix names
    most_right: Node  # next of next of...
    most_left: Node # before of before of...
    start: Node

    def __init__(self, seed: Node):
        self.start = seed
        self.most_left = self.start
        self.most_right = self.start
        self.parallel = None

    def push_right(self, data):
        old_most_right = self.most_right
        self.most_right = self.most_right.insert_right(data)
        self.most_right.left = old_most_right
        return self.most_right

    def push_left(self, data):
        old_most_left = self.most_left
        self.most_left = self.most_left.insert_left(data)
        self.most_left.right = old_most_left
        return self.most_left

class LastUpdateRecode:
    original_pit_node: Node
    original_stones: int
    parallel_orig_stones: int = 0
    another_turn: bool

class on_bottun:
    is_on: bool = False


class Pit(Button, HoverBehavior):
    # move data to the manager
    # not contol others pits

    stones_text: Label = ObjectProperty(None, allownone=True)
    stones: int = -1
    pit_type: int = -1 # 0, 1 for users jackpot. 2, 3 for regular pits
    manager = None
    return_recode: LastUpdateRecode = LastUpdateRecode()
    on_buttom: on_bottun

    def init(self, manager, mutex, on_b):
        self.stones = START_STONES_PER_JACKPOT if self.pit_type < 2 else START_STONES_PER_PIT
        self.update_text()
        self.manager = manager
        self.mutex = mutex
        self.on_buttom = on_b

    def set_stones(self, stones: int):
        self.pit_manager.stones = stones
        self.update_text()

    def add_stone(self):
        self.pit_manager.stones += 1

    def is_empty(self) -> bool:
        return self.stones == 0

    def on_press(self):
        if self.mutex.locked():
            self.mutex.release()

        self.manager.confirm_move(self.return_recode)


    def on_enter(self):
        if not self.disabled:
            print("enter", hex(id(self)))
            #self.mutex.acquire()
            self.on_buttom.is_on = True
            thread = Thread(target = self.manager.show_move, args = (self, self.return_recode))
            thread.start()

            #self.return_recode = self.manager.show_move(self)

    def on_leave(self):
        if not self.disabled:
            self.on_buttom.is_on = False
            print("leave", hex(id(self)))
            self.manager.cancel_move(self.return_recode)
            #self.mutex.release()

    def update_text(self):
        self.stones_text.text = str(self.stones)

class Player:
    jackpot: Pit
    pits: List[Pit]  # P1 : lefter the zeroes. [0] top right button, [5] top left button
                     # [0] top right up, [5] top left up
    id: int

def print_memory(object, name="", end="\n"):
    print(name, hex(id(object)), end=end)


class TurnManager():
    # lists of all users pits
    # link list for pits

    stones_in_hand = 0
    now_turn = True
    player_one: Player
    player_two: Player
    pits_list: List[Pit]
    pits_link_list: LinkList
    mutex: Lock
    # player hover
    # show the update number and color if needed: the
    # change , if have another turn and if eat stones.
    # press: make turn. reset colors
    # exit: reset colors and deUpdate stones.

    def __init__(self, pits: List[Pit], title_text):
        """
        :param pits: first is player one jackpot. last is player two jackpot
        """
        self.mutex = Lock()
        self.pits_list = pits
        self.player_one = Player()
        self.player_two = Player()
        self.title_text = title_text


        self.player_one.id = 0
        self.size_of_pits = len(pits)
        self.player_one.jackpot = pits[0]
        self.player_one.pits = pits[1:self.size_of_pits//2]  # todo check this

        self.player_two.id = 1
        self.player_two.jackpot = pits[-1]
        self.player_two.pits = pits[self.size_of_pits//2:-1]  # todo check this

        #self.player_two.pits.reverse()
        players_pits = zip(self.player_one.pits, self.player_two.pits)


        self.pits_link_list = LinkList(Node(self.player_one.jackpot))

        for player_one_pit, player_two_pit in players_pits:
            player_two_pit.pit_type = PIT_TYPES_CODES[1]
            most_right = self.pits_link_list.push_right(player_one_pit)
            most_left = self.pits_link_list.push_left(player_two_pit)
            most_left.parallel = most_right
            most_right.parallel = most_left

        self.pits_link_list.push_right(self.player_two.jackpot)

        link_list = self.pits_link_list

        # make circle
        link_list.most_right.right = link_list.most_left
        link_list.most_left.left = link_list.most_right

        self.set_turn(self.now_turn, Node)

    def do_disabled_player(self, player, disable: bool):
        player = self.get_player(player)
        for pit in player.pits:

            pit.disabled = disable or pit.stones == 0


        player.jackpot.disabled = True

    def have_stones(self, player):
        player = self.get_player(player)

        fil = lambda x: x.stones != 0
        return len(list(filter(fil, player.pits))) > 0


    def set_turn(self, now_turn, original_pit: Pit):
        # show the visual (who play pic and more)
        # and wait for input form buttons
        #todo
        self.now_turn = now_turn

        print("Turn is:", self.now_turn)
        self.do_disabled_player(now_turn, False)

        if original_pit is not Node:
            print("checkWin", end=" ")
            last_played = original_pit in self.get_player(True).pits
            print("last_played:", last_played)
            if not self.have_stones(last_played):
                oter_player = self.get_player(not last_played)
                my_player = self.get_player(last_played)
                for x in oter_player.pits:
                    oter_player.jackpot.stones += x.stones
                    x.stones = 0
                    x.update_text()

                oter_player.jackpot.update_text()
                # todo color

                player_one_stones = self.get_player(True).jackpot.stones
                player_two_stones = self.get_player(False).jackpot.stones


                if player_one_stones != player_two_stones:
                    self.title_text.text = "Player "
                    self.title_text.text += "One" if player_one_stones < player_two_stones else "Two"
                    self.title_text.text += " Win!"
                else:
                    self.title_text.text = "Tie!"
                print("game end")

        self.do_disabled_player(not now_turn, not False)

    def get_pit_node(self, pit: Pit) -> Node:
        played_pit: Node = self.pits_link_list.start
        while played_pit.data is not pit:
            played_pit = played_pit.right

        return played_pit

    def cancel_move(self, recode: LastUpdateRecode):
        # DeUpdate

        print("destory")

        player = self.get_player(self.now_turn)
        other = self.get_player(not self.now_turn)

        next_node = recode.original_pit_node
        next_node.data.stones = recode.original_stones
        recode.original_pit_node.data.update_text()

        for _ in range(recode.original_stones):
            next_node = next_node.right
            pit = next_node.data
            if pit is not player.jackpot:
                pit.stones -= 1
                pit.update_text()

        if next_node.data in player.pits and next_node.data.stones == 0:
            parallel_pit: Pit = next_node.parallel.data
            new_stones = parallel_pit.stones
            parallel_pit.stones = recode.parallel_orig_stones
            parallel_pit.update_text()

            if recode.parallel_orig_stones != new_stones:
                other.jackpot.stones -= recode.parallel_orig_stones
                other.jackpot.update_text()

        print("exit destory")

        self.mutex.release()

    def show_move(self, moved_pit: Pit, return_recode) -> LastUpdateRecode:
        self.mutex.acquire()

        print("build")
        # show the shit
        #return_recode = LastUpdateRecode()

        next_pit_node = self.first_stones_logic(moved_pit, return_recode)

        # last stone logic
        next_turn = self.last_stone_logic(next_pit_node, return_recode)  # make new turn

        print("exit build")

        return return_recode

    def get_next(self, pit_node: Node) -> Node:
        return pit_node.right

    def get_player(self, player: bool) -> Player:
        return self.player_one if player else self.player_two

    def get_jackpot(self, player: bool):
        return self.pits_link_list.start if player else self.pits_link_list.most_right


    def first_stones_logic(self, start_pit: Pit, recode: LastUpdateRecode) -> Node:
        other_player = self.get_player(self.now_turn)

        start_node = self.get_pit_node(start_pit)
        next_pit_node = self.get_next(start_node)
        recode.original_pit_node = start_node
        #moved_pit: Pit = next_pit_node.data
        recode.original_stones = start_pit.stones

        while start_pit.stones > 1:
            next_pit: Pit = next_pit_node.data

            # skip other_player jackpot
            if next_pit is not other_player.jackpot:
                next_pit.stones += 1
                next_pit.update_text()
                start_pit.stones -= 1
            next_pit_node = self.get_next(next_pit_node)

        # delete last stone
        start_pit.stones -= 1
        start_pit.update_text()

        return next_pit_node

    def last_stone_logic(self, last_node: Node, recode: LastUpdateRecode) -> bool:
        my_player = self.get_player(not self.now_turn)

        next_pit = last_node
        next_turn = not self.now_turn
        if next_pit.data is my_player.jackpot:
            next_turn = self.now_turn
            # todo coloR
        # if land on his empty pit
        elif next_pit.data in self.get_player(self.now_turn).pits \
                and next_pit.data.is_empty():
            # take parallel pit stones to player jackpot
            # todo coloR
            parallel_pit = last_node.parallel.data

            recode.parallel_orig_stones = parallel_pit.stones
            my_player.jackpot.stones += parallel_pit.stones
            parallel_pit.stones = 0

            parallel_pit.update_text()
            my_player.jackpot.update_text()

        next_pit.data.stones += 1
        next_pit.data.update_text()


        recode.another_turn = next_turn
        return next_turn

    def de_update_stones(self, stones: int, start_pit_node: Node):
        pass


    def confirm_move(self, rec: LastUpdateRecode):
        self.set_turn(rec.another_turn, rec.original_pit_node.data)

        #pit_node = self.get_pit_node(moved_pit)
        #next_pit_node: Node = self.get_next(pit_node)
        #moved_pit: Pit = pit_node.data


        # list index place
        #0   12  11  10  9   8   7   13
        #0   6   5   4   3   2   1   13
        # if land on jackpot get another turn




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
    def get_pits_from_object(list: List[Pit], object_parent):
        for object in object_parent.children:
            if isinstance(object, Pit):
                list.append(object)
            else:
                PlayLayout.get_pits_from_object(list, object)

    def get_pits(self) -> List[Pit]:
        return_list = []
        PlayLayout.get_pits_from_object(return_list, self)
        return return_list



class MainLayout(BoxLayout):
    pits_layout: PlayLayout
    title_text: Label

class Mangala(App):
    # todo: spaceing left to right and down
    game_layout: GridLayout
    turn_manager: TurnManager
    mutex: Lock


    def build(self):
        self.game_layout =  MainLayout()
        self.mutex = Lock()
        self.on_bottun = on_bottun()

        return self.game_layout

    def on_start(self):
        pits_list = self.game_layout.pits_layout.get_pits()

        self.turn_manager = TurnManager(pits_list, self.game_layout.title_text)

        for x in pits_list:
            x.init(self.turn_manager, self.turn_manager.mutex, self.on_bottun)

if __name__ == '__main__':
    Mangala().run()
    #while a.next_val:
        ##print(a.data_val)
        #a.next_val = a.next_val
    #while a.before_val:
        #print(a.data_val)
        #a.before_val = a.before_val
