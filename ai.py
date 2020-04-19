from data_types import PlayRecode

class AI:

    def __init__(self, turn_manager):
        self.turn_manager = turn_manager
        self.ai_player = self.turn_manager.player_two
        self.user_player = self.turn_manager.player_one

    def jackpot_change(self, pit, player: bool) -> int:
        temp_recode = PlayRecode()

        player_class = self.turn_manager.get_player(player)
        now_jack = player_class.jackpot.stones
        future_jack = 0



        self.turn_manager.make_move(pit, temp_recode)

        if not temp_recode.another_turn:
            pits, values = self.get_values()
            if len(values) > 0:
                future_jack += max(values)

        future_jack += player_class.jackpot.stones
        self.turn_manager.back_board(temp_recode)

        return future_jack - now_jack

    def get_values(self):
        fil = lambda x: x.stones != 0
        pits_to_play = list(filter(fil, self.ai_player.pits))

        list_turns = [self.jackpot_change(x, True) for x in pits_to_play]

        return pits_to_play, list_turns

    def value_of_pit(self, is_max):
        pits, values = self.get_values()

        func = max if is_max else min

        return func(values)


    def minimax(self, pit, depth, is_max):
        pits, values = self.get_values()
        if depth == 0 or len(pits) == 0: # or game win
            return self.value_of_pit(True)  # todo: value func

        func = max if is_max else min

        return_value = -1 if is_max else 200
        for pit in pits:
            return_value = func(return_value, self.minimax(pit, depth - 1, not is_max))

        return return_value

    def move_pit(self):

        pits, values = self.get_values()

        return pits[values.index(max(values))]

    def make_move(self):

        return self.move_pit()
