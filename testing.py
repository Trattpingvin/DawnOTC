import csv
from collections import defaultdict
from random import random, shuffle

import trueskill as ts

from dawnotc.classes import Match, Player


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

def get_data_csv(name): #tournament_records.csv
    """Read tournament match data and make Player objects, calculate trueskill ratings
    Return dict of Player objects, key being lowercase name of each players.
    """
    old_flag = True
    new_flag_when = "May 16 FFA"
    players = {}

    with open(name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) #discard the header

        while(True):
            match = [next(reader, None) for _ in range(4)]
            if match[3] is None: #check end of list
                return players

            tournament_name, consistency_check, participants, results = zip(*match)
            if consistency_check[0] != consistency_check[3]:
                print(tournament_name, consistency_check)
                raise ValueError("detected misaligned match")

            #do not account old tournaments, if old_flag started as True.
            if tournament_name[0] == new_flag_when: old_flag = False
            if old_flag: continue

            ts_list = []
            ref_results = refine_results(results)
            #first pass to create objects
            for n in participants:
                n = n.strip()
                nk = n.lower().strip()
                if nk not in players:
                    players[nk] = Player(n)
                elif players[nk].name != name_priority(n, players[nk].name):
                    players[nk].name = name_priority(n, players[nk].name)
                ts_list.append(((players[nk].ts),))

            #second pass to create ratings
            ts_results = ts.rate(ts_list, ranks = ref_results)
            for i, r in enumerate(ts_results):
                players[participants[i].lower().strip()].update_ts(r[0])

def refine_results(res):
    """Convert tournament records into integers for use in Trueskill rating calculation
    Get list of results, return converted list of results"""
    mapping = {'0': 1, '1': 0, '1.1':0, '1st': 0, '2nd': 1, '3rd': 2, '4th': 3}
    new_res = []
    for x in res:
        new_res.append(mapping[x])
    return new_res

def name_priority(a, b):
    """Given two strings, return one that has more uppercase.
    For example, Rhahi is prioritized over rhahi."""
    if a < b: return a
    else: return b

def get_real_participants():
    """Read participants.txt and refine/return list of the names"""
    with open("participants.txt") as f:
        data = f.readlines()

    names_strip = list(map(str.strip, data))
    return names_strip

def signups():
    """using real participants, return dict of players who have signed up for the tournament."""
    p = get_data_csv("dawnotc/tournament_records.csv")
    ns = get_real_participants()
    p_signups = {}

    for n in ns:
        nk = n.lower()
        if nk in p.keys():
            p_signups[nk] = p[nk]
        else:
            p_signups[nk] = Player(n)

    return p_signups


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
    all_p = []
    #divide according to bracket
    for v in players.values():
        b = v.bracket
        p[b].append(v)

    #assign teams as evenly as possible
    for v in p.values():
        shuffle(v)
        all_p += v
    
    for i, player in enumerate(all_p):
        player.team = (i % 4) + 1 #alters players

def generate_availability(players, d=0.8):
    for v in players.values():
        v.available = random() < d #alters players
