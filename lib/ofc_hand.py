from lib.deuces import Card, Evaluator

evaluator = Evaluator()

# Represents a hand object
class Hand:

    def __init__(self, player_name):
        self.player_name = player_name
        self.top = []
        self.middle = []
        self.bottom = []

    def add_card(self, card, hand_num):
        if hand_num == 0:
            if len(self.top) == 3:
                return False
            self.top.append(card)
        elif hand_num == 1:
            if len(self.middle) == 5:
                return False
            self.middle.append(card)
        elif hand_num == 2:
            if len(self.bottom) == 5:
                return False
            self.bottom.append(card)
        return True

    def clear(self):
        self.top = []
        self.middle = []
        self.bottom = []

    def print_hand(self):
        print(self.player_name)
        filled_top = self.top[:] + [-1 for i in range(3 - len(self.top))]
        filled_middle = self.middle[:] + [-1 for i in range(5 - len(self.middle))]
        filled_bottom = self.bottom[:] + [-1 for i in range(5 - len(self.bottom))]
        Card.print_pretty_cards(filled_top)
        Card.print_pretty_cards(filled_middle)
        Card.print_pretty_cards(filled_bottom)

    def evaluate_hand(self):
        top_count = evaluator.evaluate([], self.top)
        middle_count = evaluator.evaluate([], self.middle)
        bottom_count = evaluator.evaluate([], self.bottom)
        if not (top_count >= middle_count >= bottom_count):
            return 7463*3
        else:
            return top_count + middle_count + bottom_count

# Deals with specific evaluation of hands for scoring
def return_hand_vals(computer_hand, player_hand):
    c_top = evaluator.evaluate([], computer_hand.top)
    c_middle = evaluator.evaluate([], computer_hand.middle)
    c_bottom = evaluator.evaluate([], computer_hand.bottom)
    p_top = evaluator.evaluate([], player_hand.top)
    p_middle = evaluator.evaluate([], player_hand.middle)
    p_bottom = evaluator.evaluate([], player_hand.bottom)
    return c_top, c_middle, c_bottom, p_top, p_middle, p_bottom

def get_hand_type(cards):
    # Returns a string like 'Pair of 6s', 'Trips', 'Flush', etc.
    from lib.deuces.evaluator import Evaluator
    evaluator = Evaluator()
    if len(cards) == 3:
        # Front hand
        ranks = [Card.get_rank_int(c) for c in cards]
        rank_counts = {r: ranks.count(r) for r in set(ranks)}
        if 3 in rank_counts.values():
            return 'Trips'
        elif 2 in rank_counts.values():
            pair_rank = max(r for r, cnt in rank_counts.items() if cnt == 2)
            return f'Pair of {Card.STR_RANKS[pair_rank] + "s"}'
        else:
            return 'High Card'
    else:
        # 5-card hand
        hand_rank = evaluator.evaluate([], cards)
        class_int = evaluator.get_rank_class(hand_rank)
        class_str = evaluator.class_to_string(class_int)
        return class_str

def calculate_royalties(row, cards):
    # row: 'front', 'middle', 'back'
    # cards: list of card ints
    from lib.deuces.evaluator import Evaluator
    evaluator = Evaluator()
    if row == 'front':
        if len(cards) != 3:
            return 0, ''
        ranks = [Card.get_rank_int(c) for c in cards]
        rank_counts = {r: ranks.count(r) for r in set(ranks)}
        if 3 in rank_counts.values():
            return 10, 'Trips'
        elif 2 in rank_counts.values():
            pair_rank = max(r for r, cnt in rank_counts.items() if cnt == 2)
            if pair_rank >= 4 and pair_rank <= 7:
                return pair_rank - 3, f'Pair of {Card.STR_RANKS[pair_rank]}s'  # 6s-9s: 1-4 pts
            elif pair_rank == 8:
                return 2, 'Pair of 10s'
            elif pair_rank == 9:
                return 3, 'Pair of Jacks'
            elif pair_rank == 10:
                return 4, 'Pair of Queens'
            elif pair_rank == 11:
                return 5, 'Pair of Kings'
            elif pair_rank == 12:
                return 6, 'Pair of Aces'
        return 0, ''
    else:
        if len(cards) != 5:
            return 0, ''
        hand_rank = evaluator.evaluate([], cards)
        class_int = evaluator.get_rank_class(hand_rank)
        class_str = evaluator.class_to_string(class_int)
        if class_str == 'Straight':
            return 2, 'Straight'
        elif class_str == 'Flush':
            return 4, 'Flush'
        elif class_str == 'Full House':
            return 6, 'Full House'
        elif class_str == 'Four of a Kind':
            return 10, 'Quads'
        elif class_str == 'Straight Flush':
            # Royal flush is a straight flush with ace high
            ranks = [Card.get_rank_int(c) for c in cards]
            if set(ranks) == set([8, 9, 10, 11, 12]):
                return 25, 'Royal Flush'
            else:
                return 15, 'Straight Flush'
        return 0, ''
