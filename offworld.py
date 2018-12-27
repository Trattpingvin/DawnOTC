from collections import defaultdict
from random import choice, randint, random, shuffle

import trueskill as ts

import matchmaking
import testing
from classes import Match, Player
from parameters import *


def setup_brackets(players):
    """Create list of Players needed for rest of the program.
    Sort them using their weighted rank and assign brackets
    Alter Players.
    """
    sorted_ratings = sorted(players.items(), key=lambda kv: kv[1], reverse=True)

    for i, p in enumerate(sorted_ratings):
        #alters Players.
        p[1].bracket = max(1, assigned_max_level - i // (len(sorted_ratings) // assigned_max_level))

def run_matches(matches, mode=None):
    """Using match objects, run the matches and update player stats.
    Return dict of match statistics"""
    count = 0
    summary = {"levelup": 0, "leveldown": 0, "locked": 0}
    
    for match in matches:
        if mode == "test": match.generate_random_win()
        s = match.process_match() #alters players
        for k, v in s.items(): summary[k] += v
        count += 1
    return summary

def simulation_summary(players, summary=None, lowest_level = 1):
    brackets = [0] * max_level
    if lowest_level:
        sorted_players = sorted(players.items(), key=lambda kv:kv[1], reverse=True)
        count = 0
        for v in sorted_players:
            if v[1].bracket >= lowest_level:
                print(v[1])
                count += 1
        print("\t\t\t\t\tDisplaying {} players".format(count))

    for _, v in players.items():
        brackets[v.bracket - 1] += 1
    print("Level status:", brackets)
    if summary:
        print(summary)

def printseparator(day=None):
    middle = ""
    if day: middle = " DAY {} ".format(day)
    print()
    print("==============" + middle + "==============")
    print()
    
if __name__ == "__main__":
    data1 = testing.get_data("ABTdata1.txt")
    data2 = testing.get_data("ABTdata.txt")
    players = testing.rating_init(data1 + data2)
    setup_brackets(players) #alters players
    testing.assign_teams(players)

    #initial bracket info
    simulation_summary(players, lowest_level=None)
    
    #day 1
    printseparator(1)
    testing.generate_availability(players)
    matches = matchmaking.generate_matches(players)
    for match in matches:
        print(match)
    s = run_matches(matches, mode="test")
    simulation_summary(players, summary=s, lowest_level=1)
    
    #FIXME cannot run second match generation.
    #       it seems to run out of pool in find_best_opponents().
    #       not sure why.
    
    #day 2
    printseparator(2)
    testing.generate_availability(players)
    matches = matchmaking.generate_matches(players) #FIXME
    for match in matches:
        print(match)
    s = run_matches(matches, mode="test")
    simulation_summary(players, summary=s, lowest_level=1)


    