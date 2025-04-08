import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connections import get_connection

st.set_page_config(page_title="Player Analysis", layout="wide")
st.title("🏏 Player Analysis")

conn = get_connection()

# Load Players
@st.cache_data
def load_players():
    query = "SELECT DISTINCT player_name FROM  public.players ORDER BY player_name"
    df = pd.read_sql(query, conn)
    return df['player_name'].tolist()

players = load_players()
selected_player = st.selectbox("Select Player", players)

role = st.radio("Select Role", ['Batter', 'Bowler', 'All-Rounder'])
home_away = st.radio("Select Match Type", ['All', 'Home', 'Away'])

# # Career Summary
# @st.cache_data
# def player_career_summary(player_name):
#     query = f"""
#         SELECT COUNT(DISTINCT match_id) AS matches, 
#                SUM(runs_batter) AS runs, 
#                COUNT(CASE WHEN wicket = TRUE THEN 1 END) AS wickets
#         FROM deliveries
#         WHERE batter = '{player_name}' OR bowler = '{player_name}'
#     """
#     return pd.read_sql(query, conn).iloc[0]

# summary = player_career_summary(selected_player)
# st.subheader("Player Career Summary")
# k1, k2, k3 = st.columns(3)
# k1.metric("Matches", summary['matches'])
# k2.metric("Runs Scored", summary['runs'])
# k3.metric("Wickets Taken", summary['wickets'])

# Runs Per Over Phase
@st.cache_data
def runs_per_over_phase(player_name):
    query = f"""
        SELECT 
            CASE 
                WHEN over_number <= 6 THEN 'Powerplay'
                WHEN over_number >= 7 AND over_number <=15 THEN 'Middle Overs'
                ELSE 'Death Overs'
            END AS phase, 
            SUM(runs_batter) AS runs
        FROM  public.deliveries
        WHERE batter = '{player_name}'
        GROUP BY phase
    """
    return pd.read_sql(query, conn)

st.subheader("Runs by Over Phase")
over_phase_df = runs_per_over_phase(selected_player)
fig = px.bar(over_phase_df, x='phase', y='runs', color='phase', text='runs')
st.plotly_chart(fig, use_container_width=True)

# Season-wise Performance
@st.cache_data
def season_wise_performance(player_name):
    query = f"""
        SELECT m.season, SUM(d.runs_batter) AS runs, 
               COUNT(CASE WHEN d.wicket = TRUE THEN 1 END) AS wickets
        FROM  public.deliveries d
        JOIN  public.matches m USING(match_id)
        WHERE batter = '{player_name}' OR bowler = '{player_name}'
        GROUP BY m.season
        ORDER BY m.season
    """
    return pd.read_sql(query, conn)

st.subheader("Season-wise Performance")
season_df = season_wise_performance(selected_player).fillna(0)
fig = px.line(season_df, x='season', y=['runs', 'wickets'], markers=True)
st.plotly_chart(fig, use_container_width=True)

# Dismissal Types
@st.cache_data
def dismissal_types(player_name):
    query = f"""
        SELECT dismissal_kind, COUNT(*) AS count
        FROM  public.deliveries
        WHERE batter = '{player_name}' AND dismissal_kind IS NOT NULL
        GROUP BY dismissal_kind
    """
    return pd.read_sql(query, conn)

st.subheader("Dismissal Types")
dismissal_df = dismissal_types(selected_player)
fig = px.pie(dismissal_df, names='dismissal_kind', values='count')
st.plotly_chart(fig, use_container_width=True)

# Boundary Analysis
@st.cache_data
def boundary_analysis(player_name):
    query = f"""
        SELECT 
            SUM(CASE WHEN runs_batter = 4 THEN 1 ELSE 0 END) AS Fours,
            SUM(CASE WHEN runs_batter = 6 THEN 1 ELSE 0 END) AS Sixes
        FROM  public.deliveries
        WHERE batter = '{player_name}'
    """
    return pd.read_sql(query, conn).iloc[0]

st.subheader("Boundary Analysis")
b = boundary_analysis(selected_player)
k1, k2 = st.columns(2)
k1.metric("4's Hit", b['fours'])
k2.metric("6's Hit", b['sixes'])

# Strike Rate by Phase
@st.cache_data
def strike_rate_by_phase(player_name):
    query = f"""
        SELECT 
            CASE 
                WHEN over_number <= 6 THEN 'Powerplay'
                WHEN over_number >= 7 AND over_number <=15 THEN 'Middle Overs'
                ELSE 'Death Overs'
            END AS phase, 
            ROUND(SUM(runs_batter)*100.0/COUNT(*),2) AS strike_rate
        FROM  public.deliveries
        WHERE batter = '{player_name}'
        GROUP BY phase
    """
    return pd.read_sql(query, conn)

st.subheader("Strike Rate by Over Phase")
sr_df = strike_rate_by_phase(selected_player)
fig = px.bar(sr_df, x='phase', y='strike_rate', color='phase', text='strike_rate')
st.plotly_chart(fig, use_container_width=True)

# Player's Top Venues
@st.cache_data
def player_top_venues(player_name):
    query = f"""
        SELECT venue, COUNT(DISTINCT match_id) AS matches
        FROM  public.deliveries d
        JOIN  public.matches m USING(match_id)
        WHERE batter = '{player_name}' OR bowler = '{player_name}'
        GROUP BY venue
        ORDER BY matches DESC
        LIMIT 5
    """
    return pd.read_sql(query, conn)

st.subheader("Top Venues Played")
venue_df = player_top_venues(selected_player)
fig = px.bar(venue_df, x='venue', y='matches', text='matches')
st.plotly_chart(fig, use_container_width=True)

# Player vs Bowler Head-to-Head
@st.cache_data
def player_vs_bowler(player_name):
    query = f"""
        SELECT bowler, SUM(runs_batter) AS runs, COUNT(*) AS balls_faced
        FROM public.deliveries d
        WHERE batter = '{player_name}'
        GROUP BY bowler
        ORDER BY runs DESC
        LIMIT 5
    """
    return pd.read_sql(query, conn)

st.subheader("Player vs Bowler - Head to Head")
h2h_df = player_vs_bowler(selected_player)
fig = px.bar(h2h_df, x='bowler', y='runs', text='runs')
st.plotly_chart(fig, use_container_width=True)

