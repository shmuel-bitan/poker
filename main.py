import random
import os
from collections import Counter

# Définir les cartes et les valeurs
suits = ['♥', '♦', '♣', '♠']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A']
deck = [f'{value}{suit}' for value in values for suit in suits]
value_ranking = {str(i): i for i in range(2, 11)} # Convertir '2'-'10' en entiers
value_ranking.update({'V': 11, 'D': 12, 'R': 13, 'A': 14})


# Joueurs (inclut les bots)
class Player:
    def __init__(self, name, chips, is_bot=False):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
        self.is_bot = is_bot  # Détermine si le joueur est un bot

    def bet(self, amount):
        if amount > self.chips:
            amount = self.chips  # All-in
        self.chips -= amount
        self.current_bet += amount
        return amount

    def reset_bet(self):
        self.current_bet = 0

    def make_decision(self, highest_bet, table_cards, phase):
        """La logique de décision des bots."""
        if self.folded or self.chips == 0:
            return  # Ne fait rien si le bot s'est couché ou est à court de jetons

        hand_strength = self.evaluate_hand_strength(table_cards)
        if phase == 'flop' or phase == 'turn' or phase == 'river':
            if hand_strength == 'pair_or_better':
                raise_amount = min(10 * (1 + random.randint(0, 2)), self.chips)  # Raise entre 10 et 30
                return 'r', raise_amount
            elif hand_strength == 'strong_card':
                return 'c', highest_bet  # Suivre si carte > 10
            else:
                return 'f', 0  # Se coucher
        return 'c', highest_bet  # Par défaut, suivre

    def evaluate_hand_strength(self, table_cards):
        """Évalue la force de la main du bot."""
        card_values = [card[:-1] for card in self.cards]  # Extraire les valeurs des cartes
        card_ranks = [value_ranking[cv] for cv in card_values]

        # Vérifie si le bot a une paire ou mieux
        if card_ranks[0] == card_ranks[1]:
            return 'pair_or_better'

        # Vérifie si l'une des cartes a une valeur supérieure à 10
        if any(rank > 10 for rank in card_ranks):
            return 'strong_card'

        return 'weak_hand'


# Initialiser le jeu
def initialize_game(num_players):
    random.shuffle(deck)
    players = []

    for i in range(num_players):
        name = input(f"Nom du joueur {i + 1} (ou tapez 'bot' pour ajouter un bot) : ")
        is_bot = name.lower() == 'bot'
        players.append(Player(name=f'Player {i + 1}' if is_bot else name, chips=1000, is_bot=is_bot))

    # Complète avec des bots si le nombre de joueurs est inférieur à 5
    while len(players) < 5:
        players.append(Player(name=f'Bot {len(players) + 1}', chips=1000, is_bot=True))

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
def betting_round(players, minimum_bet, table_cards, phase):
    highest_bet = minimum_bet
    pot = 0
    for player in players:
        if player.folded or player.chips == 0:
            continue

        if player.is_bot:
            # Prise de décision automatique pour les bots
            decision, amount = player.make_decision(highest_bet, table_cards, phase)
            if decision == 'f':
                player.folded = True
                print(f'{player.name} has folded.')
            elif decision == 'r':
                highest_bet = player.bet(amount)
                print(f'{player.name} has raised to {highest_bet}.')
            elif decision == 'c':
                player.bet(highest_bet)
                print(f'{player.name} has called the bet of {highest_bet}.')
        else:
            # Effacer le terminal avant chaque action de joueur
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f'{player.name}, it\'s your turn. Your cards: {player.cards} | Table: {" ".join(table_cards)}')
            print(f'Highest bet: {highest_bet}. You have {player.chips} chips.')
            action = input("Do you want to (c)all, (r)aise, or (f)old? ").lower()

            if action == 'f':
                player.folded = True
            elif action == 'r':
                raise_amount = int(input("How much do you want to raise? "))
                highest_bet = player.bet(highest_bet + raise_amount)
            elif action == 'c':
                player.bet(highest_bet)
            else:
                print("Invalid action. Folding by default.")
                player.folded = True

        # Ajoute la mise au pot
        pot += player.current_bet
        print(pot)
        # Nettoyer le terminal après chaque tour (joueur ou bot)
        os.system('clear' if os.name == 'posix' else 'cls')

    return pot, highest_bet


# Afficher la table
def display_table(table_cards):
    print("Table: " + " ".join(table_cards))


# Vérifier combien de joueurs ont encore des jetons
def active_players_with_chips(players):
    return [player for player in players if player.chips > 0 and not player.folded]


# Évaluer la meilleure main d'un joueur
def evaluate_hand(player, table_cards):
    all_cards = player.cards + table_cards
    values = [card[:-1] for card in all_cards]
    suits = [card[-1] for card in all_cards]

    value_counts = Counter(values)
    suit_counts = Counter(suits)

    # Chercher les paires, brelans, etc.
    pairs = [value for value, count in value_counts.items() if count == 2]
    triples = [value for value, count in value_counts.items() if count == 3]
    quads = [value for value, count in value_counts.items() if count == 4]

    # Straight (suite) et flush (couleur) vérifications
    is_flush = any(count >= 5 for count in suit_counts.values())
    sorted_ranks = sorted([value_ranking[val] for val in values], reverse=True)
    is_straight = len(set(sorted_ranks)) >= 5 and max(sorted_ranks) - min(sorted_ranks[:5]) == 4

    # Déterminer la main
    if quads:
        return (7, max(quads))  # Carré
    elif triples and pairs:
        return (6, max(triples))  # Full
    elif is_flush:
        return (5, max(sorted_ranks))  # Couleur
    elif is_straight:
        return (4, max(sorted_ranks))  # Suite
    elif triples:
        return (3, max(triples))  # Brelan
    elif len(pairs) == 2:
        return (2, max(pairs))  # Double paire
    elif pairs:
        return (1, max(pairs))  # Paire
    else:
        return (0, max(sorted_ranks))  # Carte haute


# Trouver le gagnant en fonction des mains
def determine_winner(players, table_cards):
    best_player = None
    best_hand = (-1, -1)

    for player in players:
        print(player.name,"a les cartes", player.cards)
        if player.folded:
            continue
        player_hand = evaluate_hand(player, table_cards)
        if player_hand > best_hand:
            best_hand = player_hand
            best_player = player

    return best_player


# Main loop
def poker_game():
    num_players = int(input("Combien de joueurs humains participent (maximum 5) ? "))
    players = initialize_game(num_players)

    # Boucle principale du jeu : continue tant que plus d'un joueur a des jetons
    while len(active_players_with_chips(players)) > 1:
        random.shuffle(deck)  # Remélanger les cartes pour chaque partie
        deal_cards(players)  # Redistribuer les cartes aux joueurs
        table_cards = []
        pot = 0

        # Réinitialiser les statuts et mises des joueurs
        for player in players:
            player.folded = False
            player.reset_bet()

        # Tour pré-flop
        print("### Pre-Flop ###")
        display_players(players)
        betting_round(players, minimum_bet=10, table_cards=table_cards, phase='pre-flop')[0]

        # Flop
        table_cards += [deck.pop(), deck.pop(), deck.pop()]
        print("\n### Flop ###")
        display_table(table_cards)
        betting_round(players, minimum_bet=20, table_cards=table_cards, phase='flop')[0]

        # Turn
        table_cards.append(deck.pop())
        print("\n### Turn ###")
        display_table(table_cards)
        print("le pot est de ", pot)
        betting_round(players, minimum_bet=20, table_cards=table_cards, phase='turn')[0]

        # River
        table_cards.append(deck.pop())
        print("\n### River ###")
        display_table(table_cards)
        pot += betting_round(players, minimum_bet=20, table_cards=table_cards, phase='river')[0]

        # Déterminer le gagnant et lui attribuer le pot
        winner = determine_winner(players, table_cards)
        if winner:
            print(f"\n{winner.name} wins the pot of {pot} chips!")
            winner.chips += pot

        # Éliminer les joueurs qui n'ont plus de jetons
        players = [player for player in players if player.chips > 0]

        # Vérifier si on continue ou si un joueur a gagné
        if len(active_players_with_chips(players)) < 2:
            break

        # Fin du tour : Réinitialiser les cartes du deck pour un nouveau round
        deck.extend(table_cards)  # Remettre les cartes de la table dans le deck
        for player in players:
            deck.extend(player.cards)  # Remettre les cartes des joueurs dans le deck

    # Fin du jeu
    winner = active_players_with_chips(players)[0]
    print(f"\nGame over! {winner.name} wins with {winner.chips} chips!")


# Lancer le jeu
if __name__ == "__main__":
    poker_game()
