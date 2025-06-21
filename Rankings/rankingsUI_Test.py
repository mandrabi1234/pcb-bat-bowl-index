import sys
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from datetime import date

# Add your project module paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Factor Calculations')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Rankings')))

# Import custom modules
from data_cleaning import *
from constants import *
from constants_t20 import *
import constants_t20 as t20
import aggregations as agg 
import factors_t20 as ft20
import rankings_t20 as rank_t20

# Load and preprocess data
df = pd.read_csv(r"C:\Users\mohia\OneDrive\Documents\GitHub\pcb-rankings-ui\data\Filtered PCB Player Data - Final 582025.csv")
player_mapping = pd.read_csv(r"C:\Users\mohia\OneDrive\Documents\GitHub\pcb-rankings-ui\data\player_mapping.csv")

data_preprocessing(df)

# Filter for T20 matches only
df = df[df["Tournament"].str.contains("t20", case=False, na=False)].copy()

st.set_page_config(layout="wide")
st.title("PCB Player Rankings – Customize Your Own Weights")

# Select Batting or Bowling
ranking_type = st.selectbox("Select Ranking Type", ["Batting", "Bowling"])

# Sidebar inputs
weights = {}

with st.sidebar:
    st.header("Adjust Factor Weights")

    if ranking_type == "Batting":
        weights["strike_rate"] = st.slider("Strike Rate", 0.0, 1.0, 0.2)
        weights["tournament"] = st.slider("Tournament Calibre", 0.0, 1.0, 0.2)
        weights["opposition"] = st.slider("Opponent Strength", 0.0, 1.0, 0.2)
        weights["bat_pos"] = st.slider("Batting Position", 0.0, 1.0, 0.2)
        weights["special_bat"] = st.slider("Special Batting Talent", 0.0, 1.0, 0.2)
    else:
        weights["special_bowl"] = st.slider("Special Bowling Talent", 0.0, 1.0, 0.3)
        weights["dismissed_pos"] = st.slider("Dismissals by Batter Position", 0.0, 1.0, 0.3)
        weights["econ_rate"] = st.slider("Economy Rate", 0.0, 1.0, 0.3)

# Trigger rankings calculation
if st.button("Calculate"):
    if ranking_type == "Batting":
        # Apply and weight batting factor columns
        ft20.strike_rate_factor(df, "Runs Made", "Balls Consumed", "SR Factor")
        df["SR Factor"] *= weights["strike_rate"]

        ft20.tournament_calibre_factor(df, "Tournament", "Tournament Factor")
        df["Tournament Factor"] *= weights["tournament"]

        ft20.opp_quality_factor(df, "Team Standing", "Opposition Standing", "Opposition Factor")
        df["Opposition Factor"] *= weights["opposition"]

        ft20.batting_position_factor(df, "Runs Made", "Batting Position", "Bat Pos Factor")
        df["Bat Pos Factor"] *= weights["bat_pos"]

        ft20.special_bat_talent_factor(df, "Special Batting Talent", "Special Bat Factor")
        df["Special Bat Factor"] *= weights["special_bat"]

        # Aggregate and rank
        df_bat_agg = agg.add_runvalues(
            df,
            "Runs Avg",
            "Run Value",
            "Run Value Avg",
            "Innings Played",
            "Player ID",
            "Runs Made",
            "Dismissed",
            ["SR Factor", "Tournament Factor", "Opposition Factor", "Bat Pos Factor", "Special Bat Factor"]
        )
        rankings = rank_t20.batting_rankings(df_bat_agg, "Run Value", "Run Value Avg")

    else:
        # Apply and weight bowling factors
        ft20.special_bowl_talent_factor(df, "Special Bowling Talent", "Special Bowl Factor")
        df["Special Bowl Factor"] *= weights["special_bowl"]

        ft20.batters_dismissed_position_factor(df, "Wickets Taken", "Batters Dismissed", "Wicket Pos Value")
        df["Wicket Pos Value"] *= weights["dismissed_pos"]

        ft20.economy_rate_factor(df, "Runs Given", "Balls Bowled", "Econ Rate Factor")
        df["Econ Rate Factor"] *= weights["econ_rate"]

        df["Innings Played"] = df.groupby("Player ID")["Match ID"].transform("count")

        df_bowl_agg = agg.add_wicketvalues(
            df,
            "Wickets Avg",
            "Wicket Value",
            "Wicket Value Avg",
            "Player ID",
            "Innings Played",
            "Balls Bowled",
            "Wickets Taken",
            ["Special Bowl Factor", "Wicket Pos Value", "Econ Rate Factor"]
        )
        rankings = rank_t20.bowling_rankings(df_bowl_agg, "Wicket Value", "Wicket Value Avg")

    # Map player names and show rankings
    id_to_name = pd.Series(player_mapping["Player Name"].values, index=player_mapping["Player ID"]).to_dict()
    rankings["Player Name"] = rankings["Player ID"].map(id_to_name)
    rankings = rankings[["Player Name"] + [col for col in rankings.columns if col != "Player Name"]]

    st.dataframe(rankings)
