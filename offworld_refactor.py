import trueskill as ts
from collections import defaultdict

def get_data(name):
    with open(name) as f:
        raw_matches = f.readlines()
        #raw_matches = [l.lower() for l in lines]
    
    matches = []
    for i in range(0, len(raw_matches), 4): #gets 4 lines in a bunch
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


def weight_star_bracket(players):
    """Create list of obejcts needed for rest of the program
    get ratings: sort it using their weighted rank, and assign brackets, etc.
    return dict of Player() objects.
    """

    #sorting data to divide brackets
    sorted_ratings = sorted(players.items(), key=lambda kv: kv[1], reverse=True)

    #assign brackets, stars, and re-append trueskill rating.
    #also appended ratings so that it's easier to integrate with phil's ranks if needed.
    for i, p in enumerate(sorted_ratings):
        p[1].bracket = max(1, assigned_max_level - i // (len(sorted_ratings) // assigned_max_level))
    """
    #preview of data
    for _, v in players.items():
        print(v)
        pass
    """
    return players

class Player:
    sigma_weight = 2 #Trueskill uses 3 by default; we use 2 here.

    def __init__(self, name, bracket = 1, awards = 0, team = None, ts = ts.Rating()):
        self.name = name
        self.bracket = bracket
        self.stars = starting_stars
        self.awards = awards
        self.team = team
        self.ts = ts
        self.rnk = ts.mu - self.sigma_weight * ts.sigma

    def __repr__(self):
        a = "{:12.12} | ".format(self.name)
        b = "{:d}/{} ".format(self.bracket, max_level)
        c = "[{:{s}}] ".format('*'*self.stars, s=max_star)
        d = "Awards:{:2} | ".format(self.awards)
        e = "Team: {} | ".format(self.team)
        f = "TS: {}".format(round(self.rnk,3))
        return a+b+c+d+e+f
    
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

    def update_ts(self, r):
        self.ts = r
        self.rnk = r.mu - self.sigma_weight * r.sigma


def run_a_match(match, p):
    """given single match data, return resulting player information.
    get [[list of players], [list of win data]]
    return dictionary of players with updated bracket
    """
    players, wins = match
    players = [n.lower() for n in players]
    players_ts = [(p[n].ts,) for n in players]
    rating_result = ts.rate(players_ts, ranks=wins)
    for i, r in enumerate(rating_result):
        p[ players[i] ].update_ts(r[0])

    for idx, name in enumerate(players):
        my_level = p[n].bracket
        my_stars = p[n].stars
        my_stars_before = my_stars
        other_level = max([p[n].bracket for n in players[:idx] + players[idx+1:]])
        #winner_level = p[players[wins.index(0)]].bracket
        awards = 0

        if wins[idx] == 0: #win
            #default bonus + bonus for defeating higher level player
            high_level_bonus = max(0, other_level - my_level)
            my_stars += win_bonus + high_level_bonus
            if high_level_bonus > 0:
                awards += 1

        elif wins[idx] == 1: #lose
            #default malus
            my_stars += lose_malus #+ min(0, winner_level - my_level)

        if my_stars < 0:
            #only lose a level when lost at star 0.
            if my_stars_before == 0 and my_level > locked_level:
                    my_stars = default_lose_star
                    my_level = my_level - 1
                    leveldown += 1
            else:
                my_stars = 0
                locked += 1

        elif my_stars > max_star:
            #star_overflow = max_star - my_stars
            #if my_level == 1: print("level up!")
            if my_level == max_level:
                #awards += 1
                my_stars = max_star
            else:
                my_stars = default_win_star
                my_level = my_level + 1
                levelup += 1

        p[name].bracket = my_level
        p[name].stars = my_stars
        p[name].awards += awards

    

def simulate_matches(matches, p):
    count = 0
    levelup = 0
    leveldown = 0
    locked = 0

    for match in matches:
        players, wins = match
        brackets = [ p[name][0] for name in players ]
        #p[name]: 0: bracket 1: star 2: medals 3: truskill rating 4: weighted rating

        for idx, name in enumerate(players):
            my_level = p[name][0]
            my_stars = p[name][1]
            my_stars_before = my_stars
            other_level = max(brackets[:idx] + brackets[idx+1:])
            winner_level = p[players[wins.index(0)]]
            awards = 0

            if wins[idx] == 0: #win
                #default bonus + bonus for defeating higher level player
                high_level_bonus = max(0, other_level - my_level)
                my_stars += win_bonus + high_level_bonus
                if high_level_bonus > 0:
                    awards += 1

            elif wins[idx] == 1: #lose
                #default malus
                my_stars += lose_malus #+ min(0, winner_level - my_level)

            if my_stars < 0:
                #only lose a level when lost at star 0.
                if my_stars_before == 0 and my_level > locked_level:
                        my_stars = default_lose_star
                        my_level = my_level - 1
                        leveldown += 1
                else:
                    my_stars = 0
                    locked += 1

            elif my_stars > max_star:
                #star_overflow = max_star - my_stars
                #if my_level == 1: print("level up!")
                if my_level == max_level:
                    #awards += 1
                    my_stars = max_star
                else:
                    my_stars = default_win_star
                    my_level = my_level + 1
                    levelup += 1
                

            p[name][0] = my_level
            p[name][1] = my_stars
            p[name][2] += awards
        count += 1

    return p, [count, levelup, leveldown, locked]

def analyze_results(data):
    brackets = [0] * max_level
    awards = 0
    for _, v in data.items():
        brackets[v[0] - 1] += 1
        awards += v[2]
        
    print("Level status:", brackets, "from 1 to 5")
    print("Awards:", awards)

#control constants
max_level = 5 #number of brackets
assigned_max_level = 3
locked_level = 1 #cannot drop below this level

max_star = 3
starting_stars = 2 #default stars given at start
default_lose_star = 3
default_win_star = 1

win_bonus = 2
lose_malus = -1


""" TODO
    Matchmaking (spits out new matches using the current brackets & availability)
    Winner Simulation (spits out winner [] using trueskill and dice roll)
    Update Truskill data after each match
    Get feedback from SOS and AAAA (availability)
    Set time for the tournament
"""

""" PLAN
    List of players with their initial trueskill ratings
    convert them into sorted rank and assign brackets
    organize matches using availability, team composition, brackets, and randomness
    * simulation here for testing *
    get results and apply rules to adjust their brackets
"""

def generate_matches(players, availability):
    pass


if __name__ == "__main__":
    data1 = get_data("ABTdata1.txt")
    data2 = get_data("ABTdata.txt")
    players = rating_init(data1 + data2)
    weight_star_bracket(players) #alters players

    """
    for k, v in seed.items():
        #if v[0] > 0: print(v, k)
        pass

    analyze_results(seed)
    simulation_results, c = simulate_matches(data1 + data2, seed)
    print()
    for k, v in simulation_results.items():
        if v[0] > 0: print(v, k)
        pass

    analyze_results(simulation_results)
    print("Total matches:", c[0])
    print("Level Up-Down:", c[1], '/', c[2], '/ Freezed', c[3])
    """