import streamlit as st
import pandas as pd
from utils.db_connections import get_connection
from utils.queries import *
import plotly.express as px

st.set_page_config(
    page_title="Tournament Overview",
    layout="wide")

st.title("🏏 IPL Tournament Overview")

conn = get_connection()

# Fetch the data from the database
matches_df = pd.read_sql_query(total_matches_query, conn)
runs_df = pd.read_sql(total_runs_query, conn)
wickets_df = pd.read_sql(total_wickets_query, conn)
top_batter_df = pd.read_sql(top_batter_query, conn)
top_bowler_df = pd.read_sql(top_bowler_query, conn)
top_six_hitters_df = pd.read_sql(top_six_hitter_query, conn)
top_four_hitters_df = pd.read_sql(top_four_hitter_query, conn)
top_dot_balls_df = pd.read_sql(most_dot_balls_query, conn)
season_runs_wickets_df = pd.read_sql(season_runs_wickets_query, conn)
toss_df = pd.read_sql(toss_winner_query, conn)
total_catches_df = pd.read_sql(dismissal_types_query, conn)
top_fielders_df = pd.read_sql(caught_fielders_query, conn)
pom_df = pd.read_sql(player_of_the_match_query, conn)


# Tournament Summary
st.markdown("## Tournament Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total Matches", matches_df['total_matches'][0])
col2.metric("Total Runs Scored", runs_df['total_runs'][0])
col3.metric("Total Wickets Taken", wickets_df['total_wickets'][0])

st.markdown("---")

# Season Wise Analysis
st.markdown("## Season-wise Performance")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Total Runs per Season")
    fig1 = px.line(season_runs_wickets_df, x='season', y='total_runs', markers=True, title="Runs Trend")
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader("Total Wickets per Season")
    fig2 = px.line(season_runs_wickets_df, x='season', y='total_wickets', markers=True, title="Wickets Trend")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Top Performers
col6, col7 = st.columns(2)

with col6:
    st.subheader("🏅 Top Run Scorer")
    st.table(top_batter_df)

with col7:
    st.subheader("🔥 Top Wicket Taker")
    st.table(top_bowler_df)

col8, col9 = st.columns(2)

with col8:
    st.subheader("⚡ Top Six Hitters")
    st.table(top_six_hitters_df)

with col9:
    st.subheader("🚀 Top Four Hitters")
    st.table(top_four_hitters_df)

st.markdown("---")

# Dot Balls
st.subheader("🟢 Most Dot Balls by Bowlers")
st.table(top_dot_balls_df)

st.markdown("---")

# Additional Visualizations
st.markdown("## Visual Insights")

col10, col11 = st.columns(2)

with col10:
    st.subheader("Top Batter Contribution %")
    fig3 = px.pie(top_batter_df, names='batter', values='runs', title="Run Contribution")
    st.plotly_chart(fig3, use_container_width=True)

with col11:
    st.subheader("Top Bowler Contribution %")
    fig4 = px.pie(top_bowler_df, names='bowler', values='wickets', title="Wicket Contribution")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Runs vs Wickets Scatter
st.subheader("Seasonal Runs vs Wickets Distribution")
fig5 = px.scatter(season_runs_wickets_df, x='total_runs', y='total_wickets', color='season',
                  size='total_runs', hover_name='season',
                  title="Runs vs Wickets per Season")
st.plotly_chart(fig5, use_container_width=True)

# Toss Win Conversion %
toss_df['conversion_%'] = round((toss_df['matches_won_after_toss'] / toss_df['toss_won']) * 100, 2)

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Catches", total_catches_df['total_catches'][0])
col2.metric("Best Toss to Win Conversion %", f"{toss_df['conversion_%'].max()}%")
col3.metric("Most Player of the Match Awards", f"{pom_df['awards'].max()} by {pom_df['player_of_match'][0]}")

st.markdown("---")

# Toss Win vs Match Win Chart
fig = px.bar(toss_df, x="team", y=["toss_won", "matches_won_after_toss"],
             barmode="group", title="Toss Won vs Matches Won After Toss")

st.plotly_chart(fig, use_container_width=True)

# Toss Win Conversion % Chart
fig2 = px.bar(toss_df, x="team", y="conversion_%", title="Toss Win Conversion % by Team",
              color="conversion_%", color_continuous_scale="Viridis")

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Top Fielders with Most Catches
st.subheader("Top Fielders with Most Catches")
st.table(top_fielders_df)

st.markdown("---")

# Player of the Match Leaders
st.subheader("Top Players with Most Player of the Match Awards")
st.table(pom_df)