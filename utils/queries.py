total_matches_query = """
SELECT COUNT(*) AS total_matches FROM public.matches;
"""

total_runs_query = """
SELECT SUM(runs_total) AS total_runs FROM public.deliveries;
"""

total_wickets_query = """
SELECT COUNT(*) AS total_wickets FROM public.deliveries WHERE wicket = TRUE;
"""

top_batter_query = """
SELECT batter AS Batter, SUM(runs_batter) AS Runs 
FROM public.deliveries 
GROUP BY batter 
ORDER BY Runs DESC 
LIMIT 5;
"""

top_bowler_query = """
SELECT bowler AS Bowler, COUNT(*) AS Wickets 
FROM public.deliveries 
WHERE wicket = TRUE
GROUP BY bowler 
ORDER BY Wickets DESC 
LIMIT 5;
"""

top_six_hitter_query = """
SELECT batter AS Batter, COUNT(*) AS Sixes
FROM public.deliveries 
WHERE runs_batter = 6
GROUP BY batter
ORDER BY Sixes DESC
LIMIT 5;
"""
top_four_hitter_query = """
SELECT batter AS Batter, COUNT(*) AS Fours
FROM public.deliveries 
WHERE runs_batter = 4
GROUP BY batter
ORDER BY Fours DESC
LIMIT 5;
"""

most_dot_balls_query = """
SELECT bowler AS Bowler, COUNT(*) AS Dots
FROM public.deliveries 
WHERE runs_batter = 0 
AND runs_extras = 0
GROUP BY bowler
ORDER BY Dots DESC
LIMIT 5;
"""

season_runs_wickets_query = """SELECT 
    season, 
    SUM(runs_batter + runs_extras ) AS total_runs,
    COUNT(deliveries.batter) AS total_wickets
FROM public.deliveries
JOIN  public.matches ON deliveries.match_id = matches.match_id
GROUP BY season
ORDER BY season;
"""

toss_winner_query = """
SELECT
    team_1 as team,
    COUNT(*) AS toss_won,
    SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS matches_won_after_toss
FROM public.matches
GROUP BY team_1;
"""

dismissal_types_query = """
SELECT COUNT(*) AS total_catches
FROM public.deliveries
WHERE dismissal_kind = 'caught';
"""

caught_fielders_query = """
SELECT fielder,COUNT(*) AS catches
FROM public.deliveries
WHERE dismissal_kind = 'caught' AND fielder IS NOT NULL
GROUP BY fielder
ORDER BY catches DESC
LIMIT 5;
"""

player_of_the_match_query = """
SELECT player_of_match, COUNT(*) AS awards
FROM public.matches
GROUP BY player_of_match
ORDER BY awards DESC
LIMIT 5;
"""


highest_scoring_venue_query = """
SELECT venue, SUM(runs_total) AS total_runs
FROM public.deliveries d
JOIN matches m ON d.match_id = m.match_id
GROUP BY venue;
"""

venue_wickets_query = """
SELECT venue, COUNT(*) AS total_wickets
FROM public.deliveries d
JOIN matches m ON d.match_id = m.match_id
WHERE dismissal_kind IS NOT NULL
GROUP BY venue;
"""

venue_toss_query = """
SELECT venue, toss_decision AS decision, COUNT(*) AS count
FROM public.matches
GROUP BY venue, toss_decision;
"""

venue_runs_query = """
SELECT venue, ROUND(AVG(total_runs)/2,2) AS avg_score
FROM (
    SELECT m.match_id, venue, SUM(runs_total) AS total_runs
    FROM public.deliveries d
    JOIN public.matches m ON d.match_id = m.match_id
    GROUP BY m.match_id, venue
) sub
GROUP BY venue;
"""