import random
from itertools import combinations
import tkinter as tk

CATEGORY_NAMES = [
    "High Card",
    "Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
    "Royal Flush"
]

RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}

def parse_card(card_str):
    card_str = card_str.strip()
    if not card_str:
        return None
    suit = card_str[-1].lower()
    rank = card_str[:-1].upper()
    if suit not in ['c', 'd', 'h', 's']:
        return None
    if rank in RANK_VALUES:
        value = RANK_VALUES[rank]
    else:
        return None
    return (value, suit)

def evaluate_5_cards(cards):
    ranks = sorted([r for (r, s) in cards])
    suits = [s for (r, s) in cards]
    flush = len(set(suits)) == 1
    unique_ranks = set(ranks)
    straight = False
    high_straight_rank = None
    if len(unique_ranks) == 5:
        rmin, rmax = min(unique_ranks), max(unique_ranks)
        if rmax - rmin == 4:
            straight = True
            high_straight_rank = rmax
        else:
            if 14 in unique_ranks:
                alt_ranks = [1 if x == 14 else x for x in unique_ranks]
                alt_ranks.sort()
                if alt_ranks[-1] - alt_ranks[0] == 4 and len(set(alt_ranks)) == 5:
                    straight = True
                    high_straight_rank = 5
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    four_of_kind = None
    three_of_kind = None
    pairs = []
    for r, count in rank_counts.items():
        if count == 4:
            four_of_kind = r
        elif count == 3:
            three_of_kind = r
        elif count == 2:
            pairs.append(r)
    pairs.sort(reverse=True)
    if straight and flush:
        if high_straight_rank == 14:
            return (9,)
        else:
            return (8, high_straight_rank)
    if four_of_kind is not None:
        kicker = [r for r in ranks if r != four_of_kind][0]
        return (7, four_of_kind, kicker)
    if three_of_kind is not None and len(pairs) >= 1:
        pair_rank = max(pairs)
        return (6, three_of_kind, pair_rank)
    if flush:
        return (5, *sorted(ranks, reverse=True))
    if straight:
        return (4, high_straight_rank)
    if three_of_kind is not None:
        kickers = sorted([r for r in ranks if r != three_of_kind], reverse=True)
        return (3, three_of_kind, kickers[0], kickers[1])
    if len(pairs) >= 2:
        high_pair, low_pair = pairs[0], pairs[1]
        kicker = max([r for r in ranks if r != high_pair and r != low_pair])
        return (2, high_pair, low_pair, kicker)
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return (1, pair, kickers[0], kickers[1], kickers[2])
    return (0, *sorted(ranks, reverse=True))

def evaluate_best_hand(cards):
    n = len(cards)
    if n >= 5:
        best_rank = None
        for combo in combinations(cards, 5):
            rank = evaluate_5_cards(list(combo))
            if best_rank is None or rank > best_rank:
                best_rank = rank
        return best_rank
    else:
        rank_counts = {}
        for (r, s) in cards:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        counts = sorted(rank_counts.values(), reverse=True)
        if counts and counts[0] == 4:
            rank = [r for r, c in rank_counts.items() if c == 4][0]
            return (7, rank)
        if counts and counts[0] == 3:
            rank = [r for r, c in rank_counts.items() if c == 3][0]
            others = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return (3, rank, *others)
        if len([c for c in counts if c == 2]) >= 2:
            pair_ranks = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            return (2, pair_ranks[0], pair_ranks[1])
        if counts and counts[0] == 2:
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            others = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return (1, pair_rank, *others)
        return (0, *sorted(rank_counts.keys(), reverse=True))

def count_outs(user_cards, known_board, deck):
    known_cards = user_cards + known_board
    current_rank = evaluate_best_hand(known_cards)
    current_category = current_rank[0]
    outs_count = 0
    for card in deck:
        new_known = known_cards + [card]
        new_rank = evaluate_best_hand(new_known)
        if new_rank[0] > current_category:
            outs_count += 1
    return outs_count

def calculate_odds():
    error_label.config(text="")
    output_label.config(text="")
    my_cards_list = my_cards_entry.get().strip().split()
    flop_list = flop_entry.get().strip().split()
    turn_list = turn_entry.get().strip().split()
    river_list = river_entry.get().strip().split()
    if len(my_cards_list) != 2:
        error_label.config(text="X Please provide exactly 2 cards for your hand.")
        return
    if not (len(flop_list) == 0 or len(flop_list) == 3):
        error_label.config(text="X Please provide either 3 flop cards or leave flop empty.")
        return
    if not (len(turn_list) == 0 or len(turn_list) == 1):
        error_label.config(text="X Please provide at most 1 turn card.")
        return
    if not (len(river_list) == 0 or len(river_list) == 1):
        error_label.config(text="X Please provide at most 1 river card.")
        return
    if len(turn_list) == 1 and len(flop_list) < 3:
        error_label.config(text="X You cannot specify a Turn card without a full Flop.")
        return
    if len(river_list) == 1 and (len(flop_list) < 3 or len(turn_list) < 1):
        error_label.config(text="X You cannot specify a River card without Flop and Turn.")
        return

    user_cards, board_cards = [], []
    for cs in my_cards_list:
        card = parse_card(cs)
        if card is None:
            error_label.config(text=f"X Invalid card: {cs}")
            return
        user_cards.append(card)
    for cs in flop_list + turn_list + river_list:
        card = parse_card(cs)
        if card is None:
            error_label.config(text=f"X Invalid card: {cs}")
            return
        board_cards.append(card)
    all_known_cards = user_cards + board_cards
    if len(set(all_known_cards)) != len(all_known_cards):
        error_label.config(text="X Duplicate card detected in input.")
        return
    try:
        players = int(players_entry.get())
    except ValueError:
        error_label.config(text="X Please enter a valid number of players (1-9).")
        return
    if players < 1 or players > 9:
        error_label.config(text="X Please enter a valid number of players (1-9).")
        return
    opponents = players - 1
    known_board_count = len(board_cards)
    missing_board_count = 5 - known_board_count
    hidden_cards_count = opponents * 2
    deck = [(r, s) for r in range(2, 15) for s in ['c', 'd', 'h', 's'] if (r, s) not in all_known_cards]

    simulations = sim_var.get()
    win_count = 0
    tie_count = 0
    category_counts = [0] * len(CATEGORY_NAMES)
    current_best_rank = evaluate_best_hand(user_cards + board_cards)
    current_category = current_best_rank[0]
    current_hand_name = CATEGORY_NAMES[current_category]
    outs_count = 0
    if missing_board_count > 0:
        outs_count = count_outs(user_cards, board_cards, deck)

    for _ in range(simulations):
        drawn_cards = random.sample(deck, missing_board_count + hidden_cards_count)
        full_board = board_cards + drawn_cards[:missing_board_count]
        opp_cards = drawn_cards[missing_board_count:]
        user_final_rank = evaluate_best_hand(user_cards + full_board)
        user_cat_index = user_final_rank[0]
        category_counts[user_cat_index] += 1
        best_opp_rank = None
        for i in range(opponents):
            opp_hand = [opp_cards[2 * i], opp_cards[2 * i + 1]]
            opp_final_rank = evaluate_best_hand(opp_hand + full_board)
            if best_opp_rank is None or opp_final_rank > best_opp_rank:
                best_opp_rank = opp_final_rank
        if opponents == 0 or user_final_rank > best_opp_rank:
            win_count += 1
        elif user_final_rank == best_opp_rank:
            tie_count += 1

    win_percentage = (win_count / simulations) * 100
    tie_percentage = (tie_count / simulations) * 100
    hidden_info = f"(including {hidden_cards_count} hidden card" + ("s" if hidden_cards_count != 1 else "") + ")"
    output_lines = [
        f"Players: {players} {hidden_info}",
        f"Current hand: {current_hand_name}",
        f"Outs: {outs_count} card" + ("s" if outs_count != 1 else "") + " improve your hand",
        "",
        "Chances for each hand (simulation):"
    ]
    for cat_index in range(len(CATEGORY_NAMES) - 1, -1, -1):
        count = category_counts[cat_index]
        percent = (count / simulations) * 100
        label = "Very rare" if percent < 5.0 and count > 0 else "Good hit" if percent >= 30.0 else ""
        line = f"{CATEGORY_NAMES[cat_index]}: {count}x ({percent:.2f}%)"
        if label:
            line += f" - {label}"
        output_lines.append(line)
    output_lines += ["", f"Chance to win: {win_percentage:.2f}%", f"Chance to tie: {tie_percentage:.2f}%"]
    output_label.config(text="\n".join(output_lines))

# GUI
root = tk.Tk()
root.title("Poker Odds and Outs Simulator")
tk.Label(root, text="Your cards:").grid(row=0, column=0, sticky="w")
my_cards_entry = tk.Entry(root, width=20)
my_cards_entry.grid(row=0, column=1, columnspan=2, sticky="w")
tk.Label(root, text="Flop:").grid(row=1, column=0, sticky="w")
flop_entry = tk.Entry(root, width=20)
flop_entry.grid(row=1, column=1, columnspan=2, sticky="w")
tk.Label(root, text="Turn:").grid(row=2, column=0, sticky="w")
turn_entry = tk.Entry(root, width=20)
turn_entry.grid(row=2, column=1, columnspan=2, sticky="w")
tk.Label(root, text="River:").grid(row=3, column=0, sticky="w")
river_entry = tk.Entry(root, width=20)
river_entry.grid(row=3, column=1, columnspan=2, sticky="w")
tk.Label(root, text="Number of players:").grid(row=4, column=0, sticky="w")
players_entry = tk.Entry(root, width=5)
players_entry.grid(row=4, column=1, sticky="w")

# Legend
legend_frame = tk.Frame(root)
legend_frame.grid(row=5, column=0, columnspan=3, sticky="w", padx=10, pady=(5, 0))
tk.Label(legend_frame, text="🃏 Input format guide:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
tk.Label(legend_frame, text="Format: Rank + Suit (e.g. Ah = Ace of hearts, 10c = Ten of clubs)", fg="gray").pack(anchor="w")
tk.Label(legend_frame, text="Separate each card with a space (e.g. Ah Kh or 10c Jd Qs)", fg="gray").pack(anchor="w")
tk.Label(legend_frame, text="Suits: h = hearts, d = diamonds, c = clubs, s = spades", fg="gray").pack(anchor="w")
tk.Label(legend_frame, text="Ranks: 2–10, J, Q, K, A", fg="gray").pack(anchor="w")

# Monte Carlo options
sim_var = tk.IntVar(value=10000)
sim_frame = tk.Frame(root)
sim_frame.grid(row=6, column=0, columnspan=3, sticky="w")
for val in [1000, 5000, 10000, 100000]:
    tk.Radiobutton(sim_frame, text=f"Monte Carlo ({val})", variable=sim_var, value=val).pack(side="left")

tk.Button(root, text="Calculate odds", command=calculate_odds).grid(row=7, column=0, columnspan=3, pady=5)
error_label = tk.Label(root, text="", fg="red")
error_label.grid(row=8, column=0, columnspan=3, sticky="w")
output_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
output_label.grid(row=9, column=0, columnspan=3, sticky="w")
root.mainloop()
