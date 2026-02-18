
import random
import itertools

# Reference: http://norvig.com/poker.html

def get_rank_value(rank_char):
    """Convert rank character to integer value."""
    ranks = '..23456789TJQKA'
    if rank_char in ranks:
        return ranks.index(rank_char)
    return 0

def get_suit_value(suit_char):
    """Convert suit character to standard format or integer."""
    # Not strictly needed for rank comparison but useful for debugging
    return suit_char

def parse_card(card_str):
    """Parse a card string like 'HA' (Heart Ace), 'S7' (Spade 7), 'CT' (Club Ten).
    Returns a tuple (rank_value, suit_char).
    """
    if len(card_str) != 2:
        raise ValueError(f"Invalid card string: {card_str}")
    
    first = card_str[0].upper()
    second = card_str[1].upper()
    
    ranks = '..23456789TJQKA'
    suits = 'HSCD'
    
    # Try parsing as SuitRank (HA) - Original format
    if first in suits and second in ranks:
        return (get_rank_value(second), first)
        
    # Try parsing as RankSuit (AH) - Frontend/User format
    elif first in ranks and second in suits:
        return (get_rank_value(first), second)
        
    else:
        raise ValueError(f"Invalid card format: {card_str} (Expected SuitRank e.g. 'HA' or RankSuit e.g. 'AH')")

def hand_rank(hand):
    """Return a value indicating the ranking of a hand."""
    ranks = sorted([parse_card(c)[0] for c in hand], reverse=True)
    suits = [parse_card(c)[1] for c in hand]
    
    if len(set(suits)) == 1: # Flush
        if ranks == [14, 13, 12, 11, 10]: # Royal Flush
            return (9, ranks)
        if is_straight(ranks): # Straight Flush
            return (8, ranks)
        return (5, ranks) # Flush
        
    if len(set(ranks)) == 2: # Four of a Kind or Full House
        counts = {r: ranks.count(r) for r in ranks}
        four = [r for r in counts if counts[r] == 4]
        three = [r for r in counts if counts[r] == 3]
        two = [r for r in counts if counts[r] == 2]
        
        if four:
            return (7, four + list(set(ranks) - set(four)))
        if three and two:
            return (6, three + two)
            
    if is_straight(ranks):
        return (4, ranks)
        
    counts = {r: ranks.count(r) for r in ranks}
    three = [r for r in counts if counts[r] == 3]
    two = [r for r in counts if counts[r] == 2]
    
    if three:
        return (3, three + list(set(ranks) - set(three)))
        
    if len(two) == 2:
        return (2, sorted(two, reverse=True) + list(set(ranks) - set(two)))
        
    if len(two) == 1:
        return (1, two + list(set(ranks) - set(two)))
        
    return (0, ranks)

def is_straight(ranks):
    """Return True if the ordered ranks form a 5-card straight."""
    if len(set(ranks)) != 5:
        return False
    return (max(ranks) - min(ranks) == 4) or (ranks == [14, 5, 4, 3, 2]) # Wheel: A-5

def best_hand(cards):
    """From a list of 7 cards (2 hole + 5 community), return the best 5-card hand."""
    current_best = None
    current_best_rank = (-1, [])
    
    # Generate all combinations of 5 cards from the available cards
    # cards input is a list of strings like ['HA', 'S7', ...]
    all_combinations = itertools.combinations(cards, 5)
    
    for combo in all_combinations:
        rank = hand_rank(combo)
        if rank > current_best_rank:
            current_best_rank = rank
            current_best = combo
            
    rank_names = [
        "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
        "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
    ]
    
    return {
        "best_hand": list(current_best),
        "rank_value": current_best_rank[0],
        "rank_name": rank_names[current_best_rank[0]],
        "rank_tuple": current_best_rank
    }

def compare_hands(hand1_cards, hand2_cards, community_cards):
    """Compare two sets of hole cards with community cards."""
    best1 = best_hand(hand1_cards + community_cards)
    best2 = best_hand(hand2_cards + community_cards)
    
    if best1["rank_value"] > best2["rank_value"]:
        return 1, best1["rank_name"]
    elif best2["rank_value"] > best1["rank_value"]:
        return 2, best2["rank_name"]
    else:
        # Tie-breaker logic (compare ranks within the category)
        # Assuming rank_value includes the tie-breaking kickers in the tuple comparison
        # But my simplified return above only returned the int category.
        # Let's re-evaluate using the full tuple for comparison.
        
        # Simplified for now: just return the int result
        # To be robust, we need to compare the tuples returned by hand_rank()
        
        # Re-calc full rank tuples
        rank1 = (-1, [])
        for combo in itertools.combinations(hand1_cards + community_cards, 5):
            r = hand_rank(combo)
            if r > rank1: rank1 = r
            
        rank2 = (-1, [])
        for combo in itertools.combinations(hand2_cards + community_cards, 5):
            r = hand_rank(combo)
            if r > rank2: rank2 = r
            
        if rank1 > rank2:
            return 1, best1["rank_name"]
        elif rank2 > rank1:
            return 2, best2["rank_name"]
        else:
            return 0, best1["rank_name"] # Tie

def calculate_probability(my_cards, community_cards, num_players, num_simulations=1000):
    """Monte Carlo simulation to determine win probability."""
    deck = []
    for s in 'HSCD':
        for r in '23456789TJQKA':
            card = s + r
            if card not in my_cards and card not in community_cards:
                deck.append(card)
                
    wins = 0
    ties = 0
    
    for _ in range(num_simulations):
        random.shuffle(deck)
        
        # Deal to opponents
        opponents_cards = []
        current_deck_idx = 0
        for _ in range(num_players - 1): # Me + opponents
            opp_hand = [deck[current_deck_idx], deck[current_deck_idx+1]]
            current_deck_idx += 2
            opponents_cards.append(opp_hand)
            
        # Deal remaining community cards
        needed_community = 5 - len(community_cards)
        sim_community = list(community_cards) + deck[current_deck_idx : current_deck_idx + needed_community]
        
        my_rank = (-1, [])
        for combo in itertools.combinations(my_cards + sim_community, 5):
            r = hand_rank(combo)
            if r > my_rank: my_rank = r
            
        best_opp_rank = (-1, [])
        for opp_hand in opponents_cards:
            opp_r = (-1, [])
            for combo in itertools.combinations(opp_hand + sim_community, 5):
                r = hand_rank(combo)
                if r > opp_r: opp_r = r
            if opp_r > best_opp_rank:
                best_opp_rank = opp_r
                
        if my_rank > best_opp_rank:
            wins += 1
        elif my_rank == best_opp_rank:
            ties += 1
            
    return {
        "win": wins / num_simulations,
        "tie": ties / num_simulations,
        "lose": (num_simulations - wins - ties) / num_simulations
    }
