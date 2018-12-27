from classes import Player, Match
from random import shuffle, random
from collections import defaultdict
import trueskill as ts

def get_data(name):
    """Read match data from previous tournaments. Return match information. (old)
    For testing purposes only.
    Uses lowercase letters, which may be undesirable in real uses.
    """
    with open(name) as f:
        raw_matches = f.readlines()
    
    matches = []
    for i in range(0, len(raw_matches), 4): 
        #get 4 lines in a bunch
        a = raw_matches[i].split()
        b = raw_matches[i + 1].split()
        c = raw_matches[i + 2].split()
        d = raw_matches[i + 3].split()

        for j in range(0,8,2):
            players = [a[j], b[j], c[j], d[j]]
            wins = [1-int(a[j+1]), 1-int(b[j+1]), 1-int(c[j+1]), 1-int(d[j+1])] #0 is win, 1 is lose.
            matches.append([players, wins])
    return matches

def rating_init(matches):
    """Given matches (old) and results, return dict of players and their stats.
    For testing purposes only.
    """
    players = {}

    for p, wins in matches:
        #first pass to create objects
        for name in p:
            n = name.lower()
            if n not in players:
                players[n] = Player(name)
            elif n != name: #names including uppercase
                players[n].name = name

        #second pass to create initial ratings
        participants = [(players[p[i].lower()].ts,) for i in range(4)]
        results = ts.rate(participants, ranks=wins)
        for i, r in enumerate(results):
            players[p[i].lower()].update_ts(r[0]) #rating is 1 length tuple

    return players

def assign_teams(players):
    """Given list of players with no teams assigned, randomly assign teams considering level.
    For testing purposes only."""
    p = defaultdict(list)

    #divide according to bracket
    for v in players.values():
        b = v.bracket
        p[b].append(v)

    #assign teams as evenly as possible
    for v in p.values():
        shuffle(v)
        for idx, player in enumerate(v):
            player.team = (idx % 4) + 1 #alters players

def generate_availability(players, d=0.7):
    for v in players.values():
        v.available = random() < d #alters players