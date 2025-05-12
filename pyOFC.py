from lib.deuces.card import Card
from lib.deuces.deck import Deck
from lib.decide import place_cards
from lib.ofc_hand import Hand, return_hand_vals, calculate_royalties, get_hand_type
from lib.deuces.termcolor import colored
import os
import argparse

# Contains the Game components and runs and evaluates the game itself
class Game:

    def __init__(self):
        self.computer_hand = Hand("Computer")
        self.player_hand = Hand("Player")
        self.score = 0
        self.num_hands = 0
        self.deck = Deck()
        self.explanation = ''

    def _run_x_cards(self, num_cards):
        if self.num_hands % 2 == 0:
            self._player_play(num_cards)
            self._comp_play(num_cards)
        else:
            self._comp_play(num_cards)
            self._player_play(num_cards)


    def _player_play(self, num_cards):
        message = ''
        cards = self.deck.draw(num_cards)
        cards_to_play = cards[:]
        if num_cards == 3:
            while True:
                self.print_screen()
                print("You have drawn these 3 cards:")
                Card.print_pretty_cards(cards_to_play)
                discard_inp = input("Which card would you like to discard? (1, 2, 3): ")
                if discard_inp not in ['1', '2', '3']:
                    print(colored("Invalid input. Please enter 1, 2, or 3.", "red"))
                    continue
                discard_idx = int(discard_inp) - 1
                to_place = [c for i, c in enumerate(cards_to_play) if i != discard_idx]
                # Place the two cards
                placements = []
                for idx, card in enumerate(to_place):
                    while True:
                        self.print_screen()
                        print(f"Card {idx+1} to place:")
                        Card.print_pretty_cards([card])
                        row_inp = input("Where would you like to place this card? (1=Top, 2=Middle, 3=Bottom): ")
                        if row_inp not in ['1', '2', '3']:
                            print(colored("Invalid input. Please enter 1, 2, or 3.", "red"))
                            continue
                        if not self.player_hand.add_card(card, int(row_inp)-1):
                            print(colored("Hand is full. Pick a different hand.", "red"))
                            continue
                        break
                self.print_screen()  # Show final board after both cards are placed
                break
        else:
            # Original 5-card logic
            while (not cards_to_play == []):
                inp = ''
                while inp not in ['1', '2','3', 'x']:
                    self.print_screen()
                    if message != '':
                        print(colored(message, "red"))
                    Card.print_pretty_cards(cards_to_play)
                    print("^^^^^^^^")
                    inp = input("Where would you like to place this card? (1, 2, 3 | x to reset): ")
                    if inp not in ['1', '2','3', 'x']:
                        message = "Input was not the list 1, 2, 3, x"
                if inp == 'x':
                    self.player_hand.top = [x for x in self.player_hand.top if x not in cards]
                    self.player_hand.middle = [x for x in self.player_hand.middle if x not in cards]
                    self.player_hand.bottom = [x for x in self.player_hand.bottom if x not in cards]
                    cards_to_play = cards[:]
                else:
                    if not self.player_hand.add_card(cards_to_play[0], int(inp)-1):
                        message = "Hand is full. Pick a different hand."
                    else:
                        cards_to_play = cards_to_play[1:]
                        message = ''
                if cards_to_play == []:
                    self.print_screen()  # Show final board after last card is placed
                    inp = input("Confirm and end turn? (y/n): ")
                    if inp not in 'Yy':
                        self.player_hand.top = [x for x in self.player_hand.top if x not in cards]
                        self.player_hand.middle = [x for x in self.player_hand.middle if x not in cards]
                        self.player_hand.bottom = [x for x in self.player_hand.bottom if x not in cards]
                        cards_to_play = cards[:]

    def _comp_play(self, num_cards):
        cards = self.deck.draw(num_cards)
        to_place, order, explanation = place_cards(self, cards, onecardtime=onecardtime, fivecardtime=fivecardtime, explain=explain)
        self.explanation = explanation
        for i in range(len(to_place)):
            self.computer_hand.add_card(to_place[i], order[i])

    def run_5_card(self):
        self._run_x_cards(5)

    def run_1_card(self):
        self._run_x_cards(1)

    def run_3_card_pineapple(self):
        self._run_x_cards(3)

    def evaluate_hands(self):
        # Evaluate hands
        player_raw_score = self.player_hand.evaluate_hand()
        computer_raw_score = self.computer_hand.evaluate_hand()
        # Prepare hands for display and scoring
        player_rows = [self.player_hand.top, self.player_hand.middle, self.player_hand.bottom]
        computer_rows = [self.computer_hand.top, self.computer_hand.middle, self.computer_hand.bottom]
        row_names = ['Front', 'Middle', 'Back']
        # Check for fouls
        player_foul = player_raw_score == 7463*3
        computer_foul = computer_raw_score == 7463*3
        # Calculate royalties and hand types
        player_royalties = []
        computer_royalties = []
        player_types = []
        computer_types = []
        for i, row in enumerate(['front', 'middle', 'back']):
            prow, preason = calculate_royalties(row, player_rows[i])
            crow, creason = calculate_royalties(row, computer_rows[i])
            player_royalties.append((prow, preason))
            computer_royalties.append((crow, creason))
            player_types.append(get_hand_type(player_rows[i]))
            computer_types.append(get_hand_type(computer_rows[i]))
        # Unit points
        unit_points = [0, 0, 0]
        for i in range(3):
            if player_foul and computer_foul:
                unit_points[i] = 0
            elif player_foul:
                unit_points[i] = -1
            elif computer_foul:
                unit_points[i] = 1
            else:
                pscore = self.player_hand.evaluate_hand() if i == 0 else None
                cscore = self.computer_hand.evaluate_hand() if i == 0 else None
                # Actually, use the row scores
                prow = player_rows[i]
                crow = computer_rows[i]
                from lib.deuces.evaluator import Evaluator
                evaluator = Evaluator()
                pval = evaluator.evaluate([], prow)
                cval = evaluator.evaluate([], crow)
                if cval > pval:
                    unit_points[i] = 1
                elif cval < pval:
                    unit_points[i] = -1
                else:
                    unit_points[i] = 0
        # Sweep bonus
        sweep = False
        if not player_foul and not computer_foul:
            if all(u == 1 for u in unit_points):
                sweep = 'player'
            elif all(u == -1 for u in unit_points):
                sweep = 'computer'
        # Net royalties
        player_royalty_total = sum([x[0] for x in player_royalties])
        computer_royalty_total = sum([x[0] for x in computer_royalties])
        net_royalty = player_royalty_total - computer_royalty_total
        # Net unit points
        net_unit = sum(unit_points)
        if sweep == 'player':
            net_unit += 3
        elif sweep == 'computer':
            net_unit -= 3
        # Foul handling
        if player_foul and computer_foul:
            net_unit = 0
            net_royalty = 0
        elif player_foul:
            net_unit = -6
            net_royalty = -computer_royalty_total
        elif computer_foul:
            net_unit = 6
            net_royalty = player_royalty_total
        # Update running score
        self.score += net_unit + net_royalty
        # Print table
        print("\n+--------+----------------------+--------+----------------------+--------+--------+--------+")
        print("| Row    | Player Hand         | Royalty| CPU Hand            | Royalty| Winner | Unit   |")
        print("+--------+----------------------+--------+----------------------+--------+--------+--------+")
        for i, row in enumerate(row_names):
            prow, preason = player_royalties[i]
            crow, creason = computer_royalties[i]
            winner = 'Tie'
            if unit_points[i] == 1:
                winner = 'Player'
            elif unit_points[i] == -1:
                winner = 'CPU'
            print(f"| {row:<6} | {player_types[i]:<20} | {prow:>2} {preason:<7}| {computer_types[i]:<20} | {crow:>2} {creason:<7}| {winner:<6} | {unit_points[i]:>5}  |")
        print("+--------+----------------------+--------+----------------------+--------+--------+--------+")
        print(f"| Royalties: Player {player_royalty_total}, CPU {computer_royalty_total}, Net {net_royalty:+d}")
        print(f"| Unit Points: Player {sum([1 if u==1 else 0 for u in unit_points])}, CPU {sum([1 if u==-1 else 0 for u in unit_points])}, Net {net_unit:+d}")
        if sweep:
            print(f"| Sweep Bonus: {sweep.title()} +3")
        if player_foul:
            print("| Player fouled! CPU gets +6 and all royalties.")
        elif computer_foul:
            print("| CPU fouled! Player gets +6 and all royalties.")
        print("+--------------------------------------------------------------------------+")
        print(f"| Total This Hand: {net_unit + net_royalty:+d}")
        print("+--------------------------------------------------------------------------+\n")
        # Continue as before
        inp = ''
        while (inp not in ["Y","y","N","n"]):
            inp = input("Would you like to play another hand? (y/n): ")
            if (inp in ["N","n"]):
                exit(0)
        self.explanation = ''
        self.num_hands += 1
        self.computer_hand.clear()
        self.player_hand.clear()
        self.deck.shuffle()

    def print_screen(self):
        os.system('clear')
        if self.explanation != '':
            print(self.explanation)
        name_spacing = "                                                       "
        if self.score == 0:
            player_score = " (" + str(self.score) + ")"
            computer_score = " (" + str(self.score) + ")"
            cps_len = len(" (" + str(self.score) + ")")
        elif self.score > 0:
            player_score = colored(" (+" + str(self.score) + ")", 'green')
            computer_score = colored(" (-" + str(self.score) + ")", 'red')
            cps_len = len(" (-" + str(self.score) + ")")
        else:
            player_score = colored(" (" + str(self.score) + ")", 'red')
            computer_score = colored(" (+" + str(-self.score) + ")", 'green')
            cps_len = len(" (+" + str(-self.score) + ")")
        print(colored(self.computer_hand.player_name, attrs=['bold']) + computer_score + name_spacing[len(self.computer_hand.player_name) + cps_len:] + colored(self.player_hand.player_name, attrs=['bold']) + player_score)
        filled_top_computer = self.computer_hand.top[:] + [-1 for i in range(3 - len(self.computer_hand.top))]
        filled_middle_computer = self.computer_hand.middle[:] + [-1 for i in range(5 - len(self.computer_hand.middle))]
        filled_bottom_computer = self.computer_hand.bottom[:] + [-1 for i in range(5 - len(self.computer_hand.bottom))]
        filled_top_player = self.player_hand.top[:] + [-1 for i in range(3 - len(self.player_hand.top))]
        filled_middle_player = self.player_hand.middle[:] + [-1 for i in range(5 - len(self.player_hand.middle))]
        filled_bottom_player = self.player_hand.bottom[:] + [-1 for i in range(5 - len(self.player_hand.bottom))]
        hand_pairs = [(filled_top_computer, filled_top_player), (filled_middle_computer, filled_middle_player), (filled_bottom_computer, filled_bottom_player)]
        hand_num = 1
        for hand in hand_pairs:
            spacing = "                             " if hand_num == 1 else "           "
            for i in range(6):
                print(Card.return_pretty_cards_line(hand[0], i) + spacing + Card.return_pretty_cards_line(hand[1], i) + ("".join([" " for _ in range(20)]) if hand_num == 0 else "  ") + (colored(str(hand_num), "blue") if i == 2 else " "))
            hand_num += 1
        print("".join(["_" for i in range(99)]))
            
# Runs each game in a loop
def play():
    game = Game()
    while True:
        game.run_5_card()
        for i in range(4):
            game.run_3_card_pineapple()
        # After the last player turn, if the AI didn't just play, let it play
        if game.num_hands % 2 == 0:  # If player went last
            game._comp_play(3)
        game.print_screen()  # Always show the final board before scoring
        game.evaluate_hands()

# Parses and evaluates/stores arguments given at launch
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play Open Face Chinese Poker')
    parser.add_argument('--fivecardtime', '-f', type=int, default=5, help='# of seconds used for computer to place initial cards (Default: 5)')
    parser.add_argument('--onecardtime', '-o', type=int, default=3, help='# of seconds used for computer to place subsequent cards (Default: 3)')
    parser.add_argument("-e", "--explain", action="store_true", help="Print explanation for each AI placement")
    args = parser.parse_args()
    fivecardtime = args.fivecardtime
    onecardtime = args.onecardtime
    explain = args.explain
    play()
