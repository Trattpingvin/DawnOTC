import trueskill as ts
from collections import defaultdict
from random import random, randint, shuffle
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

    return players

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
        self.available = True
        self.played_time = 0

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

    def 

def run_a_match(match, p, s):
    """given single match data, return resulting player information.
    get [[list of players], [list of win data]]
    return dictionary of players with updated bracket
    """

    #setup
    players, wins = match
    players = [n.lower() for n in players]

    #trueskill update
    players_ts = [(p[n].ts,) for n in players]
    rating_result = ts.rate(players_ts, ranks=wins)
    for i, r in enumerate(rating_result):
        p[ players[i] ].update_ts(r[0])

    #main loop
    for idx, n in enumerate(players):
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
                    s["leveldown"] += 1
            else:
                my_stars = 0
                s["locked"] += 1

        elif my_stars > max_star:
            #star_overflow = max_star - my_stars
            #if my_level == 1: print("level up!")
            if my_level == max_level:
                #awards += 1
                my_stars = max_star
            else:
                my_stars = default_win_star
                my_level = my_level + 1
                s["levelup"] += 1

        #update values
        p[n].bracket = my_level
        p[n].stars = my_stars
        p[n].awards += awards
        s["awards"] += awards

    return s

def simulate_matches(matches, p):
    count = 0
    s = {"levelup": 0, "leveldown": 0, "locked": 0, "awards": 0}
    
    for match in matches:
        run_a_match(match, p, s)
        count += 1
    return s

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

def assign_teams(players):
    p = defaultdict(list)

    #divide according to bracket
    for v in players.values():
        b = v.bracket
        p[b].append(v)

    #assign teams as evenly as possible
    for v in p.values():
        shuffle(v)
        for idx, player in enumerate(v):
            player.team = (idx % 4) + 1

def generate_availability(players, d=0.7):
    for v in players.values():
        v.available = random() < d

def get_priority(players, selected=None):
    """Given a list of players, it looks into the list and returns list of players from highest priority to lowest.
    """
    pass

def generate_a_match(pivot, players):
    """pick a starting person -- the least flexible & least played person
    look at other teams to find best match < 3 teams will try to match this person
    function: take a player, list of players in another team > return best matching player
    """

    pass

def generate_matches(players, max_matches = 10, mode="test"):
    teams = defaultdict(list)
    matches = []
    results = []

    #availability, team
    for v in players.values():
        t = v.team
        if v.available: teams[t].append(v)

    #assign FFA
    #sort teams from smallest (a) to largest (d)
    a, b, c, d = sorted(teams.values(), key=lambda kv:len(kv))
    shuffle(a)
    #HELPME tratt!

    for _ in range(max_matches):
        match = generate_a_match(players)
        matches.append(match)
        if mode == "test": #when test, it has to generate results as well.
            results.append(simulate_a_match(match))

    # in the smallest team, assign up to 8 FFA matches.
    # assigned opponents should be chosen from the similar bracket, and do so randomly.
    # rules: [a, a, a, a] OR [a, a, a-1, a-1] OR [a, a, a, a-1], decreasing priority
    #   ^ a means a player's bracket
    # 1v1 matches will be assigned to fill up (max_matches - set_matches) count of matches.
    # choose pairs and they will be assigned to 1v1s.
    # should we ask whether they would sign up for 1v1 as well during enrollment?
    return matches, results

    """
    Match generation:
        availability, team, bracket, randomness
        1. filter only available players
        2. divide into 4 teams
        3. start with team with fewest available players, assign FFA match.
        4. once a team has depleted, 1v1 match is generated.
        5. 1v1 match will always look for same bracket players first
        6. if there are so few 1v1s, some FFA matches might be converted into 2 1v1s.
    """

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
        print(summary + "\n")

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

if __name__ == "__main__":
    data1 = get_data("ABTdata1.txt")
    data2 = get_data("ABTdata.txt")
    players = rating_init(data1 + data2)
    weight_star_bracket(players) #alters players

    assign_teams(players)
    simulation_summary(players, lowest_level=None)

    #"""
    #random data simulation
    #generate_availability(players)
    #matches = generate_matches(players)
    #summary = simulate_matches(matches, players)
    #simulation_summary(players, summary=summary, lowest_level=1)

    #""
    """
    availability = generate_availability(players)
    matches = generate_matches(players, availability)
    summary = simulate_matches(matches, players)
    simulation_summary(players, summary=summary, lowest_level=1)
    """

    """
    #same data simulation
    matches = data1 + data2
    summary = simulate_matches(matches, players)
    simulation_summary(players, summary=summary, lowest_level=1)
    """