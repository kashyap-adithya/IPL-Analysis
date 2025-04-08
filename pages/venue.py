import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connections import get_connection

st.set_page_config(page_title="Venue Analysis", layout="wide")
st.title("🏟️ Venue Analysis")

conn = get_connection()

@st.cache_data
def load_venues():
    query = "SELECT DISTINCT venue FROM  public.matches ORDER BY venue"
    df = pd.read_sql(query, conn)
    return df['venue'].tolist()

venues = load_venues()

selected_venue = st.selectbox("Select Venue", venues)

@st.cache_data
def venue_summary(venue):
    query = f"""
        SELECT COUNT(DISTINCT match_id) AS matches, 
               SUM(runs_total) AS total_runs, 
               SUM(CASE WHEN winner IS NOT NULL THEN 1 ELSE 0 END) AS results_count
        FROM  public.matches m
        JOIN  public.deliveries d 
        USING(match_id)
        WHERE venue = '{venue}'
    """
    return pd.read_sql(query, conn).iloc[0]

summary = venue_summary(selected_venue)

st.subheader("Venue Summary")
k1, k2, k3 = st.columns(3)
k1.metric("Matches Played", summary['matches'])
k2.metric("Total Runs Scored", summary['total_runs'])
k3.metric("Results Decided", summary['results_count'])

@st.cache_data
def toss_decision_trend(venue):
    query = f"""
        SELECT toss_decision, COUNT(*) AS count
        FROM  public.matches
        WHERE venue = '{venue}'
        GROUP BY toss_decision
    """
    return pd.read_sql(query, conn)

st.subheader("🎲 Toss Decision Trend")
toss_df = toss_decision_trend(selected_venue)
fig = px.pie(toss_df, names='toss_decision', values='count', title='Toss Decisions')
st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def average_scores_per_innings(venue):
    query = f"""
        SELECT inning, AVG(total_runs) AS avg_runs
        FROM (
            SELECT m.match_id, inning, SUM(d.runs_batter + d.runs_extras) AS total_runs
            FROM  public.matches m
            JOIN  public.deliveries d 
            USING(match_id)
            WHERE venue = '{venue}'
            GROUP BY m.match_id, inning
        ) t
        GROUP BY inning
        ORDER BY inning
    """
    return pd.read_sql(query, conn)

st.subheader("📈 Average Score per Innings")
score_df = average_scores_per_innings(selected_venue)
st.bar_chart(score_df.set_index('inning'))

@st.cache_data
def top_performers(venue):
    query = f"""
        SELECT batter, SUM(runs_batter) AS runs
        FROM  public.deliveries d
        JOIN  public.matches m USING(match_id)
        WHERE venue = '{venue}'
        GROUP BY batter
        ORDER BY runs DESC
        LIMIT 5
    """
    return pd.read_sql(query, conn)

st.subheader("🏅 Top Run Scorers at Venue")
top_bat_df = top_performers(selected_venue)
st.table(top_bat_df)

# Batting Friendly vs Bowling Friendly Analysis
@st.cache_data
def venue_avg_runs(selected_venue):
    query = f"""
        SELECT AVG(total_runs)/2 as avg_runs_per_match
        FROM (
            SELECT match_id, SUM(runs_total) as total_runs
            FROM  public.deliveries d
            JOIN  public.matches m 
            USING(match_id)
            WHERE m.venue = '{selected_venue}'
            GROUP BY match_id
        ) sub
    """
    return pd.read_sql(query, conn).iloc[0]

venue_stats = venue_avg_runs(selected_venue)

st.subheader("🏏 Venue Scoring Stats")
st.metric("Avg Runs per Innings", round(venue_stats['avg_runs_per_match'], 2))

# Team Win % at Venue
@st.cache_data
def team_win_percentage(selected_venue):
    query = f"""
        SELECT winner, COUNT(*) AS wins
        FROM  public.matches
        WHERE venue = '{selected_venue}' AND winner IS NOT NULL
        GROUP BY winner
    """
    return pd.read_sql(query, conn)

st.subheader("🥇 Team Win % at Venue")
team_win_df = team_win_percentage(selected_venue)
fig = px.bar(team_win_df, x='winner', y='wins', title='Team Wins at Venue')
st.plotly_chart(fig, use_container_width=True)

# Toss Winner → Match Winner Conversion
@st.cache_data
def toss_to_win(selected_venue):
    query = f"""
        SELECT COUNT(*) AS toss_won,
               SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS matches_won_after_toss
        FROM  public.matches
        WHERE venue = '{selected_venue}'
    """
    return pd.read_sql(query, conn).iloc[0]

conversion = toss_to_win(selected_venue)
conversion_percent = (conversion['matches_won_after_toss'] / conversion['toss_won']) * 100 if conversion['toss_won'] > 0 else 0
st.subheader("🎲 Toss Win → Match Win Conversion %")
st.metric("Conversion %", f"{conversion_percent:.2f}%")

# Rain/Abandoned Matches
@st.cache_data
def abandoned_matches(selected_venue):
    query = f"""
        SELECT COUNT(*) AS abandoned_matches
        FROM  public.matches
        WHERE venue = '{selected_venue}' AND winner LIKE 'No Result'
    """
    return pd.read_sql(query, conn).iloc[0]

abandoned = abandoned_matches(selected_venue)
st.subheader("🌧️ Rain/Abandoned Matches")
st.metric("Abandoned Matches", abandoned['abandoned_matches'])


# Heatmap — Over-wise Runs Scored
@st.cache_data
def heatmap_data(selected_venue):
    query = f"""
        SELECT over_number, SUM(runs_total) AS runs
        FROM  public.deliveries d
        JOIN  public.matches m 
        USING(match_id)
        WHERE m.venue = '{selected_venue}'
        GROUP BY over_number
        ORDER BY over_number
    """
    return pd.read_sql(query, conn)

st.subheader("🔥 Over-wise Runs Heatmap")
heatmap_df = heatmap_data(selected_venue)
fig = px.density_heatmap(heatmap_df, x="over_number", y="runs", nbinsx=20, color_continuous_scale="Viridis")
st.plotly_chart(fig, use_container_width=True)