import trueskill as ts
from collections import defaultdict

def get_data(name):
    with open(name) as f:
        lines = f.readlines()
        lines = [l.lower() for l in lines]
    
    matches = []
    for i in range(0, len(lines), 4): #gets 4 lines in a bunch
        a = lines[i].split()
        b = lines[i + 1].split()
        c = lines[i + 2].split()
        d = lines[i + 3].split()
        for j in range(0,8,2):
            rnd = []
            rnd.append((a[j], a[j + 1])) 
            rnd.append((b[j], b[j + 1]))
            rnd.append((c[j], c[j + 1]))
            rnd.append((d[j], d[j + 1]))   
            matches.append(rnd)
    # output looks like this: [('Hexapus', '0'), ('Duban', '0'), ('Adorfield', '0'), ('MrCubez', '1')]
    return matches

def ranking(matches):
    players = defaultdict(lambda: ts.Rating())
    #maybe I should try defaultdict(lambda: ts.Rating())
    for match in matches:
        p, results_flipped = zip(*match)
        results = []
        for a in results_flipped:
            results.append(1-int(a))

        participants = [(players[p[i]],) for i in range(4)]
        results = ts.rate(participants, ranks=results)
        for idx, rating in enumerate(results):
            players[ p[idx] ] = rating[0]
    return players

def rank_using_sigma(players):
    rankings = {}
    for k, v in players.items():
        rankings[k] = v.mu - 2 * v.sigma

    sorted_by_value = sorted(rankings.items(), key=lambda kv: kv[1], reverse=True)
    return sorted_by_value

def star_division(players, div):
    players_star = {}
    bracketsize = int(len(players)/div) + 1
    current_bracket = 5
    current_count = 0
    for player in players:
        players_star[player[0]] = [current_bracket, 1, player[1]]
        current_count += 1
        if current_count == bracketsize:
            current_bracket += -1
            current_count = 0

    """
        for k, v in players_star.items():
            print(v, k)
    """
    return players_star

def run_matches(matches, p):
    run_matches = 0
    matches_in_a_week = 15

    for match in matches:
        players, results = zip(*match)
        levels = [p[name][0] for name in players]
        #p[name]: 0: bracket 1: star 2: truskill rank

        for idx, name in enumerate(players):
            my_level = levels[idx]
            other_level_max = max(levels[:idx] + levels[idx+1:])
            #winner_idx = results.index(str(1))
            #winner_name = players[winner_idx]
            #winner_level = p[winner_name][0]

            if results[idx] == '1': #winner
                #increase player's star counts
                p[name][1] += 1 + max(other_level_max - my_level, 0) #get star
                #if the player got star overflow, their rank get updated
                if p[name][1] > 2:
                    if p[name][0] == 5: p[name][1] = 2 #highest rank, max star stays
                    else: p[name][1] = 1 #new stars
                    p[name][0] = min(5, p[name][0] + 1) #increase rank


            elif results[idx] == '0':#loser
                p[name][1] += -1 #lose star
                #if my_level > winner_level: p[name][1] += -1
                
                if p[name][1] < 0:
                    if p[name][0] > 1: p[name][1] = 2 #rank drop > new star
                    else: p[name][1] = 0 #lowest rank already, no new star
                    p[name][0] = max(1, p[name][0] - 1) #decrease rank
            #FIXME REFACTOR
            else:
                raise(ValueError)
        
        run_matches += 1
        """
        if run_matches % matches_in_a_week == 0:
            for k, v in p.items():
                print(v, k)
            print()
            """

    for k, v in p.items():
            print(v, k)
        # for winner
        #   gets a star
        #   gets stars according to highest losing player
        #   


    return None

if __name__ == "__main__":
    data1 = get_data("ABTdata1.txt")
    data2 = get_data("ABTdata.txt")
    rank_init = ranking(data1 + data2)
    rankings = rank_using_sigma(rank_init)
    bracket_star = star_division(rankings, 5)
    run_matches(data1+data2, bracket_star)


def scribble():
    pass

#TODO:  use 3 weighted 1v1 to make ranks from ABTs and see how Truskill thinks.
#       print intermediate results, using arrows to indicate ups and downs?
#       player name, sigma, mu, rank_diff
#       week by week, with extra field showing comparison to previous rank. EXAMPLE: ManyCopies (4), OneCopy(-3)

#TODO:  decide how to measure MMR