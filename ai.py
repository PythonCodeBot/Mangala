from __future__ import annotations

from typing import Iterator
from copy import deepcopy

from data_types import PitData
import pit_board
import ui_board

TURNS_CALCULATE = 3  # smallest is 1


class AI:
    """
    ai logic play
    """

    def __init__(self, ui_class: ui_board.UIBoard):
        """
        init the class
        :param ui_class: the ui for passing the ui instructions
        """
        self.ui_class = ui_class

    def play(self) -> int:
        """
        play the best move
        :return: which index to play
        """
        board = self.ui_class.board_data

        #value = float("-inf")
        start_alpha = float("-inf")
        start_beta = float("inf")
        #return_index = -1
        play_index = AI.minimax(True, board, TURNS_CALCULATE, start_alpha, start_beta, True)

        #print("END")
        #for possibility in AI.get_possibilities(board, True):
        #    print("hi!1")
        #    temp_value = AI.minimax(board, TURNS_CALCULATE - 1, start_alpha, start_beta, True)

        #    if temp_value > value:
        #        return_index = possibility.index
        #        value = temp_value

        # 7 most right
        # 12 most left
        return play_index

    @staticmethod
    def make_turn(board: pit_board.PitBoard, pit_index: int) -> None:
        """
        make the move
        :param board: the board
        :param pit_index: index of playing pit
        :return: None
        """
        for _ in board.make_move(pit_index):
            pass

    @staticmethod
    def get_turn_value(board: pit_board.PitBoard) -> int:
        """
        get the turn value if the it played
        :param board: the board data
        :return: the value of the turn to the ai, how good is this turn
        """

        return_value = 0
        #
        user_player = board.get_player(True)
        ai_player = board.get_player(False)

        # get now value
        return_value += ai_player.jackpot.stones
        return_value -= user_player.jackpot.stones
            #print("ai_player:", ai_player.jackpot.stones, end=" ")
            #print("user_player:", user_player.jackpot.stones)
            #print(return_value)

        return return_value

    @staticmethod
    def get_possibilities(board: pit_board.PitBoard, which_turn: bool) -> Iterator[PitData]:
        """
        get the possible turns in the turn
        :param board: the board data
        :param which_turn: which turn is it?
        :return: the possible turns, where the pit is not zero
        """
        for pit in board.get_player(which_turn).pits:
            if pit.stones:
                yield pit

    @staticmethod
    def is_game_over(board: pit_board.PitBoard) -> bool:
        """
        return if the game over
        :param board: the data of the board
        :return: if game over
        """
        return board.have_win()

    @staticmethod
    def minimax(start, board: pit_board.PitBoard, depth: int, alpha: int, beta: int, do_max: bool) -> int:
        """
        get turns data
        :param board: the board with current pits data
        :param depth: how much turns calculate
        :param do_max: if max the return or min
        :return: the max or min value from this move
        """

        # get value of this turn
        if depth == 0 or board.have_win():
            #print("end value: ", AI.get_turn_value(board))
            return AI.get_turn_value(board)

        compare_func = max if do_max else min
        start_value_input = "-inf" if do_max else "inf"
        maxEval = float(start_value_input)
        turn = board.now_turn

        return_index = -1
        for possibility in AI.get_possibilities(board, turn):
            now_board = deepcopy(board)
            AI.make_turn(now_board, possibility.index)


            #print("depth:", depth, "check:", possibility.index, "$:")
            next_do_max = not now_board.now_turn  # if ai(false) max else min
            eval = AI.minimax(False, now_board, depth - 1, alpha, beta, next_do_max)

            if depth == TURNS_CALCULATE:
                print("check:", possibility.index, "value:", eval)
            #print("depth:", depth, "check:", possibility.index, "value:", eval)
            if depth == TURNS_CALCULATE:
                if now_board.now_turn == do_max:
                    print("get another turn")

            old_eval = maxEval
            maxEval = compare_func(eval, maxEval)

            if old_eval != maxEval:
                return_index = possibility.index

            if do_max:
                alpha = max(eval, alpha)
            else:
                beta = min(eval, beta)

            if beta <= alpha:
                return_index = possibility.index
                break

        if start:
            return return_index
        return maxEval
