import itertools
import math
from collections import defaultdict
from random import random

import trueskill as ts

from dawnotc.parameters import *


class Player:
    sigma_weight = 2 #Trueskill uses 3 by default; we use 2 here.

    def __init__(self, name, bracket = 1, awards = 0, team = None, ts = ts.Rating()):
        self.name = name
        self.team = team
        self.bracket = bracket
        self.stars = starting_stars
        
        self.wins = 0
        self.losses = 0
        self.awards = {"op":0, "nv":0, "d1":0, "d2":0, "d3":0, "d4":0}

        #matchmaking related
        self.available = True
        self.matches_played = 0
        self.matches_assigned = 0
        self.preference = [0,0,0] #0 is no info, 1 is preferred, -1 is avoided.
                                  #[Mars, Ceres, Io]

        #trueskill related
        self.ts = ts
        self.rnk = ts.mu - self.sigma_weight * ts.sigma

    def __repr__(self):
        a = "{:12.12} | ".format(self.name)
        b = "{:d}/{} ".format(self.bracket, max_level)
        c = "[{:{s}}] ".format('*'*self.stars, s=max_star)
        d = "OP Award:{:2} | ".format(self.awards["op"])
        e = "Team: {} | ".format(self.team)
        f = "TS: {:06.3f} | ".format(round(self.rnk,3))
        g = "W:{} L:{} P:{} | ".format(self.wins*3, self.losses, self.matches_played)
        h = "Availability: {} {}".format("#" if self.available else ".", self.preference)
        return a+b+c+d+e+f+g+h
    
    #compare strength of players, using bracket (primary) and rank (secondary)
    def __ge__(self, other): return self.__gt__(other) or self.__eq__(other)
    def __le__(self, other): return self.__lt__(other) or self.__eq__(other)
    def __ne__(self, other): return not self.__eq__(other)
    def __gt__(self, other): #>
        return self.bracket > other.bracket or (self.bracket == other.bracket and self.rnk > other.rnk)
    def __lt__(self, other): #<
        return self.bracket < other.bracket or (self.bracket == other.bracket and self.rnk < other.rnk)
    def __eq__(self, other): #==
        return self.bracket == other.bracket and self.rnk == other.rnk

    def get_num_matches(self):
        return self.matches_assigned+self.matches_played

    def update_ts(self, r):
        self.ts = r
        self.rnk = r.mu - self.sigma_weight * r.sigma

class Match:
    BETA = 25/6

    def __init__(self, players=None):
        self.players = []
        self.result = []
        self.notes = []
        self.location = None
        self.processed = False
        # maybe I should implement match stats here,
        # showing post-analysis information of gained stars and ranks
        if players: self.add_players(players)

    def __repr__(self):
        return repr([p.name for p in self.players])

    def add_players(self, players):
        """Get list of Player objects and add them into this match."""
        if len(self.players) + len(players) > 4:
            raise ValueError("More than 4 players are given.")
        else:
            self.players += players

    def generate_random_win(self):
        """Using the players in this match, calculate win probability and return the random winner and their index.
        For testing purposes only."""
        dice_threshold = []
        acc = 0
        for idx, p in enumerate(self.players):
            team1 = [p.ts]*3
            team2 = [v.ts for v in self.players[:idx] + self.players[idx+1:]]
            prob = self.win_probability(team1, team2)
            acc += prob
            dice_threshold.append(acc)
        
        prev = 0
        roll = random() * acc
        winner = None
        winner_idx = None

        for idx, d in enumerate(dice_threshold):
            if roll < d and roll > prev:
                self.result.append(0) #win
                winner = self.players[idx]
                winner_idx = idx
            else:
                self.result.append(1) #lose
            prev = d

        return winner, winner_idx

    def win_probability(self, team1, team2):
        """Win probability function from snippet of Trueskill documentation.
        For testing purposes only."""
        #because FFA, let's assume team1 is made of 3 identical players.
        delta_mu = sum(r.mu for r in team1*3) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1*3, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (self.BETA * self.BETA) + sum_sigma)
        t = ts.global_env()
        return t.cdf(delta_mu / denom)

    def sub(self, subout, subin): #not tested
        """Given a Player, replace them with another."""
        for idx, p in enumerate(self.players):
            if p is subout:
                subin.matches_assigned = subout.matches_assigned
                subout.matches_assigned = 0
                self.players[idx] = subin
                return
        raise ValueError("Subout player does not exist")

    def process_match(self):
        if len(self.result) != len(self.players):
            print("RESULT:", self.result, "PLAYERS:", self)
            raise ValueError("match result does not match player count")
        elif not self.processed:
            self.processed = True
            stats = defaultdict(int)
            """
            #update trueskill ratings
            players_ratings = [(p.ts,) for p in self.players]
            resulting_ratings = ts.rate(players_ratings, ranks=self.result)
            for idx, rating in enumerate(resulting_ratings):
                self.players[idx].update_ts(rating[0]) #alter player
            """
            
            #update player 
            for idx, p in enumerate(self.players):
                #setup
                my_level = p.bracket
                my_stars = p.stars
                my_stars_before = my_stars
                other_level = max([x.bracket for x in self.players[:idx] + self.players[idx+1:]])
                
                #win-lose
                if self.result[idx] == 0: #win
                    op_bonus = 1 if other_level - my_level > 0 else 0
                    my_stars += win_bonus + op_bonus
                    p.awards["op"] += op_bonus #alter Player
                    p.wins += 1 #alter player

                elif self.result[idx] == 1: #lose
                    my_stars += lose_malus
                    p.losses += 1 #alter player

                #applying results
                if my_stars < 0:
                    #if the player had no stars before, their rank falls.
                    if my_stars_before == 0:
                        my_stars = default_lose_star
                        my_level = max(locked_level, my_level - 1)
                        stats["leveldown"] += 1

                    #if the player had at least 1 star, keep the rank.
                    else:
                        my_stars = 0 #clamp stars
                        stats["locked"] += 1
                elif my_stars > max_star:
                    if my_level == max_level:
                        my_stars = max_star
                    else:
                        my_stars = default_win_star
                        my_level = min(max_level, my_level + 1)
                        stats["levelup"] += 1

                #update values
                p.bracket = my_level
                p.stars = my_stars
                p.matches_played += p.matches_assigned #not sure if this was updated or not.
                p.matches_assigned = 0

            return stats

#TODO why is this here? putting it in ifmain for now
if __name__ == '__main__':
    #Testing for win probability.
    a = Player("A", ts = ts.Rating(30,1))
    b = Player("B", ts = ts.Rating(30,10))
    c = Player("C", ts = ts.Rating(25,3))
    d = Player("D", ts = ts.Rating(25,1))
    p = [a,b,c,d]
    m = Match(p)
    x = m.generate_random_win()
    print(x)

