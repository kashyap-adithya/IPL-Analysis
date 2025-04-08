import plotly.express as px
import pandas as pd


def plot_run_progression(df):
    df['cumsum_runs'] = df.groupby('inning')['runs_total'].cumsum()
    fig = px.line(df, x=df.index, y='cumsum_runs', color='inning', markers=True, title="Run Progression")
    return fig


def plot_phase_runs(df):
    def assign_phase(over):
        if over <= 6:
            return 'Powerplay'
        elif over <= 15:
            return 'Middle Overs'
        else:
            return 'Death Overs'

    df['phase'] = df['over_number'].apply(assign_phase)
    runs_phase = df.groupby(['inning', 'phase'])['runs_total'].sum().reset_index()

    fig = px.bar(runs_phase, x='phase', y='runs_total', color='inning', barmode='group', title="Runs by Over Phases")
    return fig


def plot_worm_chart(df):
    df['cumsum_runs'] = df.groupby('inning')['runs_total'].cumsum()
    df['ball_no'] = df.groupby('inning').cumcount() + 1
    fig = px.line(df, x='ball_no', y='cumsum_runs', color='inning', markers=True, title="Worm Chart (Runs vs Balls)")
    return fig
