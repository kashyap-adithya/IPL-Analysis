import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from utils.db_connections import get_connection
from plotly.subplots import make_subplots

st.set_page_config(page_title="Team Analysis", layout="wide")

st.title("🏏 Team Analysis")

# DB connection
conn = get_connection()

# Load Teams
@st.cache_data
def load_teams():
    query = "SELECT DISTINCT team_name FROM  public.teams ORDER BY team_name"
    df = pd.read_sql(query, conn)
    return df['team_name'].tolist()

teams = load_teams()

selected_team = st.selectbox("Select Team", teams)

# Team Overview KPIs
@st.cache_data
def get_team_overview(team_name):
    query = f"""
        SELECT 
            COUNT(DISTINCT match_id) AS matches_played,
            SUM(CASE WHEN winner = '{team_name}' THEN 1 ELSE 0 END) AS wins,
            ROUND(SUM(CASE WHEN winner = '{team_name}' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT match_id), 2) AS win_pct
        FROM  public.matches
        WHERE team_1 = '{team_name}' OR team_2 = '{team_name}'
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0]

overview = get_team_overview(selected_team)

st.subheader(f"📊 {selected_team} Overview")

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Matches Played", overview['matches_played'])
kpi2.metric("Wins", overview['wins'])
kpi3.metric("Win %", overview['win_pct'])

# Top Run Scorers
@st.cache_data
def top_run_scorers(team_name):
    query = f"""
        SELECT batter, SUM(runs_batter) AS runs
        FROM  public.deliveries d
        JOIN  public.matches m ON d.match_id = m.match_id
        WHERE team_1 = '{team_name}' OR team_2 = '{team_name}'
        GROUP BY batter
        ORDER BY runs DESC
        LIMIT 5
    """
    return pd.read_sql(query, conn)

st.subheader("🏏 Top Run Scorers")
batting_df = top_run_scorers(selected_team)
fig1 = px.bar(batting_df, x='batter', y='runs', color='batter', title='Top Run Scorers', text='runs')
st.plotly_chart(fig1, use_container_width=True)

# Top Wicket Takers
@st.cache_data
def top_wicket_takers(team_name):
    query = f"""
        SELECT bowler, COUNT(*) AS wickets
        FROM  public.deliveries d
        JOIN  public.matches m ON d.match_id = m.match_id
        WHERE wicket = TRUE
          AND (team_1 = '{team_name}' OR team_2 = '{team_name}')
        GROUP BY bowler
        ORDER BY wickets DESC
        LIMIT 5
    """
    return pd.read_sql(query, conn)

st.subheader("🎯 Top Wicket Takers")
bowling_df = top_wicket_takers(selected_team)
fig2 = px.bar(bowling_df, x='bowler', y='wickets', color='bowler', title='Top Wicket Takers', text='wickets')
st.plotly_chart(fig2, use_container_width=True)

# Win Distribution by Venue
@st.cache_data
def win_distribution_by_venue(team_name):
    query = f"""
        SELECT venue, COUNT(*) AS wins
        FROM  public.matches
        WHERE winner = '{team_name}'
        GROUP BY venue
        ORDER BY wins DESC
    """
    return pd.read_sql(query, conn)

st.subheader("🏟️ Win Distribution by Venue")
venue_df = win_distribution_by_venue(selected_team)
fig3 = px.pie(venue_df, names='venue', values='wins', title='Win % by Venue')
st.plotly_chart(fig3, use_container_width=True)

# Season Wise Performance
@st.cache_data
def season_wise_performance(team_name):
    query = f"""
        SELECT season, COUNT(*) AS matches, 
        SUM(CASE WHEN winner = '{team_name}' THEN 1 ELSE 0 END) AS wins
        FROM  public.matches
        WHERE team_1 = '{team_name}' OR team_2 = '{team_name}'
        GROUP BY season
        ORDER BY season
    """
    return pd.read_sql(query, conn)

st.subheader("📈 Season-wise Performance")
season_df = season_wise_performance(selected_team)
season_df['win_pct'] = (season_df['wins'] * 100) / season_df['matches']

# Create Subplot with Secondary Y Axis
fig4 = make_subplots(specs=[[{"secondary_y": True}]])

# Add Matches Line
fig4.add_trace(
    go.Scatter(x=season_df['season'], y=season_df['matches'], name="Matches", mode='lines+markers'),
    secondary_y=False,
)

# Add Wins Line
fig4.add_trace(
    go.Scatter(x=season_df['season'], y=season_df['wins'], name="Wins", mode='lines+markers'),
    secondary_y=False,
)

# Add Win % Line (Secondary Axis)
fig4.add_trace(
    go.Scatter(x=season_df['season'], y=season_df['win_pct'], name="Win %", mode='lines+markers', line=dict(dash='dot')),
    secondary_y=True,
)

# Update Axes
fig4.update_layout(
    title_text="Season-wise Performance",
    xaxis_title="Season",
    yaxis_title="Matches / Wins",
)
fig4.update_yaxes(title_text="Win %", secondary_y=True)

st.plotly_chart(fig4, use_container_width=True)


# Toss Decision Stats
@st.cache_data
def toss_decision_stats(team_name):
    query = f"""
        SELECT toss_decision, COUNT(*) AS count
        FROM  public.matches
        WHERE toss_winner = '{team_name}'
        GROUP BY toss_decision
    """
    return pd.read_sql(query, conn)

st.subheader("🪙 Toss Decisions")
toss_df = toss_decision_stats(selected_team)
fig5 = px.pie(toss_df, names='toss_decision', values='count', hole=0.4, title='Toss Decision Split')
st.plotly_chart(fig5, use_container_width=True)
