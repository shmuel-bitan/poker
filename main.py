import random

# Définir les cartes et les valeurs
suits = ['♥', '♦', '♣', '♠']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A']
deck = [f'{value}{suit}' for value in values for suit in suits]


# Joueurs
class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False

    def bet(self, amount):
        if amount > self.chips:
            amount = self.chips  # All-in
        self.chips -= amount
        self.current_bet += amount
        return amount

    def reset_bet(self):
        self.current_bet = 0


# Initialiser le jeu
def initialize_game():
    random.shuffle(deck)
    players = [Player(f'Player {i + 1}', 1000) for i in range(5)]
    return players


# Distribuer les cartes
def deal_cards(players):
    for player in players:
        player.cards = [deck.pop(), deck.pop()]


# Afficher l'état des joueurs
def display_players(players):
    for player in players:
        status = 'folded' if player.folded else f'chips: {player.chips}, bet: {player.current_bet}'
        print(f'{player.name} - {status}')


# Tour de mise
def betting_round(players, minimum_bet):
    highest_bet = minimum_bet
    for player in players:
        if player.folded:
            continue
        print(f'{player.name}, it\'s your turn. Your cards: {player.cards}')
        print(f'Highest bet: {highest_bet}. You have {player.chips} chips.')
        action = input("Do you want to (c)all, (r)aise, or (f)old? ").lower()

        if action == 'f':
            player.folded = True
        elif action == 'r':
            raise_amount = int(input("How much do you want to raise? "))
            total_bet = highest_bet + raise_amount
            player.bet(total_bet)
            highest_bet = total_bet
        elif action == 'c':
            player.bet(highest_bet)
        else:
            print("Invalid action. Folding by default.")
            player.folded = True


# Afficher la table
def display_table(table_cards):
    print("Table: " + " ".join(table_cards))


# Main loop
def poker_game():
    players = initialize_game()
    deal_cards(players)
    table_cards = []

    # Tour pré-flop
    print("### Pre-Flop ###")
    display_players(players)
    betting_round(players, minimum_bet=10)

    # Flop
    table_cards += [deck.pop(), deck.pop(), deck.pop()]
    print("\n### Flop ###")
    display_table(table_cards)
    betting_round(players, minimum_bet=20)

    # Turn
    table_cards.append(deck.pop())
    print("\n### Turn ###")
    display_table(table_cards)
    betting_round(players, minimum_bet=20)

    # River
    table_cards.append(deck.pop())
    print("\n### River ###")
    display_table(table_cards)
    betting_round(players, minimum_bet=20)

    # Fin du jeu (pour simplifier, on n'évalue pas encore les mains ici)
    print("\n### End of Game ###")
    display_players(players)


# Lancer le jeu
if __name__ == "__main__":
    poker_game()
