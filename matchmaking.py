from collections import defaultdict
import random
import pdb
from dawnotc.classes import Match

def rank_difference(player1, player2):
    return abs(player1.bracket-player2.bracket)

def find_best_opponents(chosen_player, team):
    """ look through team to find the best opponents to chosen_player"""

    #add players, lowest rank differnce first, until we have at least two candidates

    pool = []
    note = ""
    rank_diffs = [(p, rank_difference(chosen_player, p)) for p in team]
    
    rank_diffs_sorted = sorted(rank_diffs, key=lambda tup: tup[1])
    best_matched_rank_diff_ever = rank_diffs_sorted[0][1]
    best_matched_rank_diff = rank_diffs_sorted[0][1]
    for p, rank in rank_diffs_sorted:
        if rank==best_matched_rank_diff:
            pool.append(p)
            continue
        elif len(pool)<2:
            best_matched_rank_diff = rank
            pool.append(p)
            continue
        break

    if best_matched_rank_diff_ever>=1:
        note = "Bad matching from team "+str(pool[0].team)+" because the rank difference is "+str(best_matched_rank_diff_ever)
    for player in pool:
        if rank_difference(chosen_player, player)>=best_matched_rank_diff_ever+2:
            pool.remove(player)
            print("Removed big rank difference in find_best_opponents")

    return pool, note

def find_opponents(player, otherteams):
    match = Match()
    match.players.append(player)
    notes = []
    for team in otherteams:
        assert len(team)>0
        pool, note = find_best_opponents(player, team)
        if note:
            notes.append(note)
        assert len(pool)>0
        
        least = pool[0].get_num_matches()
        chosen_players = []
        for player in pool:
            if player.get_num_matches() < least:
                least = player.get_num_matches()
        for player in pool:
            if player.get_num_matches() == least:
                chosen_players.append(player)
        
        match.players.append(random.choice(chosen_players)) #we could look at preferences here instead of just taking one at random
        # or just take the one with least amount of games played? but then we have no random factor
    match.notes = notes[:]

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

def available(avail, day):
    if isinstance(avail, int):
        days = [None, 0b1, 0b10, 0b100, 0b1000]
        return days[day]&avail
    else:
        return avail

def generate_a_match(players):
    """pick a starting person -- the least flexible & least played person
    look at other teams to find best match < 3 teams will try to match this person
    """
    teams = defaultdict(list)

    #availability, team
    for v in players.values():
        if instanceof(v.team, int): t = v.team
        else: t = v.team.id
        if v.available: teams[t].append(v)

    teams_sorted = sorted(teams.values(), key=lambda v:len(v))

    for team in teams_sorted:
        if len(team)==0:
            raise ValueError("Team has no available players")
        elif len(team)==1:
            #team has only one available player
            return find_opponents(team[0], [t for t in teams_sorted if t!=team])

   

    chosen_player = least_played(players)
    
    return find_opponents(chosen_player, [value for key, value in teams.items() if key!=chosen_player.team])


def generate_matches(players, max_matches = 10):
    """Changes player state
    """
    matches = []
    for _ in range(max_matches):
        match = generate_a_match(players)
        for player in match.players:
            player.matches_assigned += 1 #STATE CHANGE ALERT


        matches.append(match)
    return matches
