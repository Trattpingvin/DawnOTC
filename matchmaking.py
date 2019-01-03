from collections import defaultdict
import random
import pdb
from classes import Match

def rank_difference(player1, player2):
    return abs(player1.bracket-player2.bracket)

def find_best_opponents(player, team):
    """ look through team to find the best opponents to player"""

    #add players, lowest rank differnce first, until we have at least two candidates

    pool = []
    rank_diffs = [(p, rank_difference(player, p)) for p in team]
    
    rank_diffs_sorted = sorted(rank_diffs, key=lambda tup: tup[1])

    best_matched_rank = rank_diffs_sorted[0][1]
    for p, rank in rank_diffs_sorted:
        if rank==best_matched_rank:
            pool.append(p)
            continue
        elif len(pool)<2:
            best_matched_rank = rank
            pool.append(p)
            continue
        return pool 
    return pool

def find_opponents(player, otherteams):
    match = [player] 

    for team in otherteams:
        assert len(team)>0
        pool = find_best_opponents(player, team)
        assert len(pool)>0
        match.append(random.choice(pool)) #we could look at preferences here instead of just taking one at random
        # or just take the one with least amount of games played? but then we have no random factor
    if len(match)==1:
        pdb.set_trace()
    return match

def least_played(players):
    """ Out of players, return the player to be chosen as base for generating a match. Should be one with least amount of matches played.  """
    
    pool = []
    players = sorted(players.values(), key=lambda x : x.get_num_matches())#sort by least used players
    min_played = players[0].get_num_matches()
    current_played = min_played
        
    while len(players)>0 and players[0].get_num_matches()==min_played:
        pool.append(players.pop(0))

    #from the pool, find the least represented team, and if they have more than one candidate, choose the one with the most restrictive preferences
    teams = defaultdict(list) #one per team
    for player in pool:
        teams[player.team].append(player)
    teams = sorted(teams.values(), key=lambda v:len(v))

    chosen_team = teams[0]

    chosen_player = chosen_team[0]
    max_chosen_player_preference = 0
    for player in chosen_team:
        preference = player.preference.count(-1)
        if preference>max_chosen_player_preference:
            chosen_player = player
            max_chosen_player_preference = preference

    return chosen_player
  

def generate_a_match(players):
    """pick a starting person -- the least flexible & least played person
    look at other teams to find best match < 3 teams will try to match this person
    """
    teams = defaultdict(list)

    #availability, team
    for v in players.values():
        t = v.team
        if v.available: teams[t].append(v)

    teams_sorted = sorted(teams.values(), key=lambda v:len(v))

    for team in teams_sorted:
        if len(team)==0:
            raise ValueError("Team has no available players")
        elif len(team)==1:
            #team has only one available player
            return find_opponents(team[0], [t for t in teams_sorted if t!=team])

   

    chosen_player = least_played(players)
    
    return find_opponents(chosen_player, [value for key, value in teams.iteritems() if key!=chosen_player.team])


def generate_matches(players, max_matches = 10):
    """Changes player state
    """
    matches = []

    for _ in range(max_matches):
        match_raw = generate_a_match(players)
        for player in match_raw:
            player.matches_assigned += 1 #STATE CHANGE ALERT

        match = Match(match_raw)
        matches.append(match)
    return matches
