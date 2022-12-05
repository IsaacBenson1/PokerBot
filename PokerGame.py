from pypokerengine.engine.table import Table
from pypokerengine.engine.player import Player
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.game_state_utils import deepcopy_game_state

import random
from utils4e import MCT_Node, ucb
#from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate


# TODO imlement utility function and display function in GAME()

##############################################################
################## GAME ######################################
##############################################################

class PokerGame:

    def __init__(self):

       game = Game()
       game.set_game_rule(player_num=3, max_round=10, small_blind_amount=5, ante_amount=1)
       game.register_player({"uuid-1": {"name": "NEMO", "stack": 100}}, FishPlayer())
       game.register_player({"uuid-2": {"name": "DORY", "stack": 100}}, FishPlayer())
       game.register_player({"uuid-3": {"name": "MCTS", "stack": 100}}, MCTSPlayer(game))


       # 2. Setup GameState object

       initial_state = game.generate_initial_game_state(game.players_holder)
       game_state, events = game.run_until_game_finish(initial_state)

       # 3. Run simulation and get updated GameState object
       updated_state, events = game.apply_action(game_state, "call", 10)






##############################################################
################## PLAYERS   #################################
##############################################################


class MCTSPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    def __init__(self, game):
        self.game = game;
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        action, amount = monte_carlo_tree_search(round_state,self.game)
        return action,amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class FishPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

##############################################################
################## FROM AIMA CODE ############################
##############################################################

def monte_carlo_tree_search(state, game, N=1000):

    def select(n):
        """select a leaf node in the tree"""
        if n.children:
            return select(max(n.children.keys(), key=ucb))
        else:
            return n

    def expand(n):
        """expand the leaf node by adding all its children states"""
        if not n.children and not game.terminal_test(n.state):
            n.children = {MCT_Node(state=game.result(n.state, action), parent=n): action
                          for action in game.actions(n.state)}
        return select(n)

    def simulate(game, state):
        """simulate the utility of current state by random picking a step"""
        player = game.to_move(state)
        while not game.terminal_test(state):
            action = random.choice(list(game.actions(state)))
            state = game.result(state, action)
        v = game.utility(state, player)
        return -v

    def backprop(n, utility):
        """passing the utility back to all parent nodes"""
        if utility > 0:
            n.U += utility
        # if utility == 0:
        #     n.U += 0.5
        n.N += 1
        if n.parent:
            backprop(n.parent, -utility)

    root = MCT_Node(state=state)

    for _ in range(N):
        leaf = select(root)
        child = expand(leaf)
        result = simulate(game, child.state)
        backprop(child, result)

    max_state = max(root.children, key=lambda p: p.N)

    return root.children.get(max_state)
##############################################################
################## FROM AIMA CODE AND PPE ####################
######### POKER GAME PLAYABLE BY AIMA MCTS ###################
##############################################################
class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""
    def __init__(self):
        self.game_rule = {}
        self.blind_structure = {}
        self.players_holder = {}

    def actions(self, game_state):
        players = game_state["table"].seats.players
        player_pos = game_state["next_player"]
        sb_amount = game_state["small_blind_amount"]
        return ActionChecker.legal_actions(players, player_pos, sb_amount)

    def result(self, game_state, move):
        action = move[0]
        bet_amount = move[1]
        if game_state["street"] == Const.Street.FINISHED:
            game_state, events = self._start_next_round(game_state)
        updated_state, messages = RoundManager.apply_action(game_state, action, bet_amount)
        return updated_state

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, game_state, game_rule):
        is_round_finished = game_state["street"] == Const.Street.FINISHED
        is_final_round = game_state["round_count"] == game_rule["max_round"]
        is_winner_decided = len([1 for p in game_state["table"].seats.players if p.stack!=0])==1
        return is_round_finished and (is_final_round or is_winner_decided)

    def to_move(self, game_state):
        playa = game_state["next_player"]
        return playa

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))

    def run_until_round_finish(self, game_state):
        mailbox = []
        while game_state["street"] != Const.Street.FINISHED:
            next_player_pos = game_state["next_player"]
            next_player_uuid = game_state["table"].seats.players[next_player_pos].uuid
            next_player_algorithm = self.fetch_player(next_player_uuid)
            msg = MessageBuilder.build_ask_message(next_player_pos, game_state)["message"]
            action, amount = next_player_algorithm.declare_action(msg["valid_actions"], msg["hole_card"], msg["round_state"])
            game_state, messages = RoundManager.apply_action(game_state, action, amount)
            mailbox += messages
        events = [self.create_event(message[1]["message"]) for message in mailbox]
        events = [e for e in events if e]
        if self.terminal_test(game_state, self.game_rule):
            events += self._generate_game_result_event(game_state)
        return game_state, events

    def fetch_player(self, uuid):
        return self.players_holder[uuid]

    def create_event(self, message):
        message_type = message["message_type"]
        if MessageBuilder.STREET_START_MESSAGE == message_type:
            return Event.create_new_street_event(message)
        if MessageBuilder.ASK_MESSAGE == message_type:
            return Event.create_ask_player_event(message)
        if MessageBuilder.GAME_RESULT_MESSAGE == message_type:
            return Event.create_game_finish_event(message)
        if MessageBuilder.ROUND_RESULT_MESSAGE == message_type:
            return Event.create_round_finish_event(message)

    def _generate_game_result_event(self, game_state):
        dummy_config = {
                "initial_stack": None,
                "max_round": None,
                "small_blind_amount": None,
                "ante": None,
                "blind_structure": None
                }
        message = MessageBuilder.build_game_result_message(dummy_config, game_state["table"].seats)["message"]
        return [self.create_event(message)]

    def set_game_rule(self, player_num, max_round, small_blind_amount, ante_amount):
        self.game_rule["player_num"] = player_num
        self.game_rule["max_round"] = max_round
        self.game_rule["sb_amount"] = small_blind_amount
        self.game_rule["ante"] = ante_amount

    def set_blind_structure(self, blind_structure):
        self.blind_structure = blind_structure

    def register_player(self, uuid, player):
        if not isinstance(player, BasePokerPlayer):
            raise TypeError("player must inherit %s class." % BasePokerPlayer)
        self.players_holder[uuid] = player

    def generate_initial_game_state(self, players_info):
        table = Table()
        for uuid, info in players_info.items():
            table.seats.sitdown(Player(uuid, info["stack"], info["name"]))

        table.dealer_btn = len(table.seats.players)-1
        return {
            "round_count": 0,
            "small_blind_amount": self.game_rule["sb_amount"],
            "street": Const.Street.PREFLOP,
            "next_player": None,
            "table": table
        }

    def _start_next_round(self, game_state):
        game_finished = game_state["round_count"] == self.game_rule["max_round"]
        game_state, events = self.start_new_round(game_state)
        if Event.GAME_FINISH == events[-1]["type"] or game_finished:
            raise Exception("Failed to apply action. Because game is already finished.")
        return game_state, events

    def run_until_game_finish(self, game_state):
        mailbox = []
        event_box= []
        if game_state["street"] != Const.Street.FINISHED:
            game_state, events = self.run_until_round_finish(game_state)
            event_box += events
        while True:
            game_state, events = self.start_new_round(game_state)
            event_box += events
            if Event.GAME_FINISH == events[-1]["type"]: break
            game_state, events = self.run_until_round_finish(game_state)
            event_box += events
            if Event.GAME_FINISH == events[-1]["type"]: break
        event_box = [e for e in event_box if e]
        return game_state, event_box


    def start_new_round(self, game_state):
        round_count = game_state["round_count"] + 1
        ante, sb_amount = self.game_rule["ante"], self.game_rule["sb_amount"]
        deepcopy = deepcopy_game_state(game_state)
        deepcopy_table = deepcopy["table"]
        deepcopy_table.shift_dealer_btn()

        ante, sb_amount = update_blind_level(ante, sb_amount, round_count, self.blind_structure)
        deepcopy_table = exclude_short_of_money_players(deepcopy_table, ante, sb_amount)
        is_game_finished = len([1 for p in deepcopy_table.seats.players if p.is_active()])==1
        if is_game_finished: return deepcopy, self._generate_game_result_event(deepcopy)

        new_state, messages = RoundManager.start_new_round(round_count, sb_amount, ante, deepcopy_table)
        events = [self.create_event(message[1]["message"]) for message in messages]
        events = [e for e in events if e]
        return new_state, events





##############################################################
################## EVENT CLASS NEEDED FOR GAME ###############
################## FROM PPE ##################################
##############################################################



class Event:
    NEW_STREET = "event_new_street"
    ASK_PLAYER = "event_ask_player"
    ROUND_FINISH = "event_round_finish"
    GAME_FINISH = "event_game_finish"

    @classmethod
    def create_new_street_event(self, message):
        return {
                "type": self.NEW_STREET,
                "street": message["street"],
                "round_state": message["round_state"],
                }

    @classmethod
    def create_ask_player_event(self, message):
        players = message["round_state"]["seats"]
        next_player_pos = message["round_state"]["next_player"]
        asked_player_uuid = players[next_player_pos]["uuid"]
        return {
                "type": self.ASK_PLAYER,
                "uuid": asked_player_uuid,
                "valid_actions": message["valid_actions"],
                "round_state": message["round_state"]
                }

    @classmethod
    def create_round_finish_event(self, message):
        player_info = lambda info: { "uuid": info["uuid"], "stack": info["stack"] }
        return {
                "type": self.ROUND_FINISH,
                "round_state": message["round_state"],
                "winners": [player_info(info) for info in message["winners"]]
                }

    @classmethod
    def create_game_finish_event(self, message):
        player_info = lambda info: { "uuid": info["uuid"], "stack": info["stack"] }
        return {
                "type": self.GAME_FINISH,
                "players": [player_info(info) for info in message["game_information"]["seats"]]
                }


class Action:
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"

############################################################
################ GLOBAL METHODS USED IN GAME ###############
#################### AND EVENT #############################
############################################################

def update_blind_level(ante, sb_amount, round_count, blind_structure):
    level_thresholds = sorted(blind_structure.keys())
    current_level_pos = [r <= round_count for r in level_thresholds].count(True)-1
    if current_level_pos != -1:
        current_level_key = level_thresholds[current_level_pos]
        update_info = blind_structure[current_level_key]
        ante, sb_amount = update_info["ante"], update_info["small_blind"]
    return ante, sb_amount

def exclude_short_of_money_players(table, ante, sb_amount):
    sb_pos, bb_pos = _steal_money_from_poor_player(table, ante, sb_amount)
    _disable_no_money_player(table.seats.players)
    table.set_blind_pos(sb_pos, bb_pos)
    if table.seats.players[table.dealer_btn].stack == 0: table.shift_dealer_btn()
    return table

def _steal_money_from_poor_player(table, ante, sb_amount):
    players = table.seats.players
    # exclude player who cannot pay ante
    for player in [p for p in players if p.stack < ante]: player.stack = 0
    if players[table.dealer_btn].stack == 0: table.shift_dealer_btn()

    search_targets = players + players + players
    search_targets = search_targets[table.dealer_btn+1:table.dealer_btn+1+len(players)]
    # exclude player who cannot pay small blind
    sb_player = _find_first_elligible_player(search_targets, sb_amount + ante)
    sb_relative_pos = search_targets.index(sb_player)
    for player in search_targets[:sb_relative_pos]: player.stack = 0
    # exclude player who cannot pay big blind
    search_targets = search_targets[sb_relative_pos+1:sb_relative_pos+len(players)]
    bb_player = _find_first_elligible_player(search_targets, sb_amount*2 + ante, sb_player)
    if sb_player == bb_player:  # no one can pay big blind. So steal money from all players except small blind
        for player in [p for p in players if p!=bb_player]: player.stack = 0
    else:
        bb_relative_pos = search_targets.index(bb_player)
        for player in search_targets[:bb_relative_pos]: player.stack = 0
    return players.index(sb_player), players.index(bb_player)


def _find_first_elligible_player(players, need_amount, default=None):
    if default: return next((player for player in players if player.stack >= need_amount), default)
    return next((player for player in players if player.stack >= need_amount))

def _disable_no_money_player(players):
    no_money_players = [player for player in players if player.stack == 0]
    for player in no_money_players:
        player.pay_info.update_to_fold()





