import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from utils.db_connections import get_connection
from utils.plot_utils import plot_run_progression, plot_worm_chart, plot_phase_runs

st.set_page_config(page_title="Match Analysis", page_icon="⚔️", layout="wide")

st.title("⚔️ Match Analysis")
st.markdown("Deep Dive into individual IPL matches")

# Database Connection
conn = get_connection()

# Load Match List
@st.cache_data
def load_matches():
    query = "SELECT match_id, season, match_date, team_1, team_2, winner FROM  public.matches ORDER BY match_date DESC"
    return pd.read_sql(query, conn)

matches = load_matches()

match_list = matches.apply(lambda x: f"{x['season']} - {x['team_1']} vs {x['team_2']} ({x['match_date']})", axis=1)
selected_match = st.selectbox("Select a Match", match_list)

match_id = matches.loc[match_list == selected_match, "match_id"].values[0]

# Load Selected Match Data
@st.cache_data
def load_match_data(match_id):
    deliveries_query = f"SELECT * FROM  public.deliveries WHERE match_id = {match_id} ORDER BY inning, over_number, ball_number"
    deliveries = pd.read_sql(deliveries_query, conn)
    match_info_query = f"SELECT * FROM  public.matches WHERE match_id = {match_id}"
    match_info = pd.read_sql(match_info_query, conn).iloc[0]
    return deliveries, match_info

deliveries, match_info = load_match_data(match_id)

# Match Overview
st.subheader(f"{match_info['team_1']} vs {match_info['team_2']}")
st.markdown(f"**Winner:** {match_info['winner']}")
st.markdown(f"**Venue:** {match_info['venue']}, {match_info['city']}")
st.markdown(f"**Player of the Match:** {match_info['player_of_match']}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Run Progression", "Over Phase Analysis", "Worm Chart", "Advanced Analysis"])

# Tab 1 - Run Progression
with tab1:
    st.plotly_chart(plot_run_progression(deliveries), use_container_width=True)

# Tab 2 - Over Phase Analysis
with tab2:
    st.plotly_chart(plot_phase_runs(deliveries), use_container_width=True)

# Tab 3 - Worm Chart
with tab3:
    st.plotly_chart(plot_worm_chart(deliveries), use_container_width=True)

# Tab 4 - Advanced Analysis
with tab4:
    st.header("Partnership Runs")
    partnership = deliveries.groupby(['inning', 'batter', 'non_striker'])['runs_batter'].sum().reset_index()
    partnership['partnership'] = partnership['batter'] + " & " + partnership['non_striker']
    fig = px.bar(partnership, x='partnership', y='runs_batter', color='inning',
                 labels={'runs_batter': 'Runs Scored', 'partnership': 'Partnership'})
    st.plotly_chart(fig, use_container_width=True)

    st.header("Bowler Economy Heatmap")
    economy = deliveries.groupby('bowler')['runs_total'].sum() / deliveries.groupby('bowler')['ball_number'].count()
    economy = economy.reset_index(name='economy')

    fig = px.imshow(economy.sort_values('economy').T, aspect="auto", text_auto=True,
                    labels=dict(x="Bowler", y="Metric", color="Economy"))
    st.plotly_chart(fig, use_container_width=True)

    st.header("Dismissal Types Distribution")
    dismissals = deliveries[deliveries['dismissal_kind'].notnull()]
    fig = px.pie(dismissals, names='dismissal_kind', title="Dismissal Types")
    st.plotly_chart(fig, use_container_width=True)

    st.header("Wickets per Bowler")
    wickets = dismissals.groupby('bowler').size().reset_index(name='wickets')
    fig = px.bar(wickets.sort_values('wickets', ascending=True), 
                 x='wickets', y='bowler', orientation='h', color='wickets')
    st.plotly_chart(fig, use_container_width=True)

    st.header("Top Run Scorers")
    run_scorers = deliveries.groupby('batter')['runs_batter'].sum().reset_index().sort_values('runs_batter', ascending=False)
    st.dataframe(run_scorers, use_container_width=True)

    st.header("Key Moments Timeline")
    moments = deliveries[(deliveries['runs_batter'] >= 50) | (deliveries['dismissal_kind'].notnull())]
    moments['desc'] = moments.apply(
        lambda x: f"{x['batter']} 50 Runs" if x['runs_batter'] >= 50 else f"{x.get('batter', 'Unknown')} Out ({x.get('dismissal_kind', 'Unknown')})",
        axis=1
    )
    fig = px.scatter(moments, x='over_number', y='inning', text='desc',
                     labels={'over_number': 'Over', 'inning': 'Inning'}, title="Key Moments Timeline")
    st.plotly_chart(fig, use_container_width=True)
