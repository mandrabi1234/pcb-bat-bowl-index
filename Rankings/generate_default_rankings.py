from constants import *
from constants_t20 import *
import aggregations as agg
import factors_t20 as ft20
import rankings_t20 as rank_t20
from data_cleaning import *
from constants import config as rankings_config
import streamlit as st
import pandas as pd
import numpy as np

from constants_t20 import config as default_config
import copy

def generate_default_rankings(data_path, mapping_path, format_filter="t20"):
    """
    Generate default batting and bowling rankings using preset factor weights.
    
    Parameters:
        data_path (str): Path to the raw match data CSV.
        mapping_path (str): Path to the player mapping CSV.
        format_filter (str): Filter format (e.g., "t20", "list_a", "four_day").

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (batting_rankings_df, bowling_rankings_df)
    """
    config = copy.deepcopy(default_config)
    
    # Load and clean
    df = data_path
    player_mapping = mapping_path
    data_preprocessing(df)

    # Filter by match format
    df = df[df["Format"].str.lower() == format_filter.lower()]

    # --- Batting Factors ---
    ft20.strike_rate_factor(df, "Runs Made", "Balls Consumed", config["FACTOR_SR"], config)
    ft20.tournament_calibre_factor(df, "Tournament", config["FACTOR_TOURNAMENT"], config)
    ft20.opp_quality_factor(df, "Team Standing", "Opposition Standing", config["FACTOR_OPP_QUALITY"], config)
    ft20.batting_position_factor(df, "Runs Made", "Batting Position", config["FACTOR_BAT_POSITION"], config)
    ft20.special_bat_talent_factor(df, "Special Batting Talent", config["FACTOR_SPECIAL_BAT_TALENT"], config)
    


    batting_factors = [
    (config["FACTOR_SR"], config["SR_FACTOR_DEFAULT"]),
    (config["FACTOR_TOURNAMENT"], config["TOURNAMENT_FACTOR_DEFAULT"]),
    (config["FACTOR_OPP_QUALITY"], config["OPP_QUALITY_FACTOR_DEFAULT"]),
    (config["FACTOR_BAT_POSITION"], config["BATTING_POS_DEFAULT"]),
    (config["FACTOR_SPECIAL_BAT_TALENT"], config["BAT_TALENT_DEFAULT"])
    ]

    df_bat_agg = agg.add_runvalues(
        df, 
        rankings_config["RUN_AVG_COL"],
        rankings_config["RUNVALUE_COL"], 
        rankings_config["RUNVALUE_AVG_COL"],
        rankings_config["BATTING_INNINGS_PLAYED"], 
        rankings_config["PLAYER_ID"], 
        rankings_config["RUNS_MADE"], 
        rankings_config["DISMISSED_COL"], 
        rankings_config["BATTING_AVG_FACTOR"],
        rankings_config["BATTING_AVG"],
        config["BATTING_FACTOR_MIN"],
        config["BATTING_FACTOR_MAX"],
        config["BASELINE_BATTING_AVG"],
        config["FACTOR_BATTING_AVG"],
        batting_factors,
        config
    )

    df_bat_rank = rank_t20.batting_rankings(df_bat_agg, rankings_config["RUNVALUE_COL"], rankings_config["RUNVALUE_AVG_COL"])

    # --- Bowling Factors ---
    ft20.special_bat_talent_factor(df, "Special Bowling Talent", config["FACTOR_SPECIAL_BOWL_TALENT"], config)
    ft20.batters_dismissed_position_factor(df, "Wickets Taken", "Batters Dismissed", config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], config)
    ft20.economy_rate_factor(df, "Runs Given", "Balls Bowled", config["FACTOR_ECON_RATE"], config)

    bowling_factors = [
    (config["FACTOR_ECON_RATE"], config["ECON_RATE_FACTOR_DEFAULT"]),
    (config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], config["WICKET_BAT_POS_DEFAULT"]),
    (config["FACTOR_TOURNAMENT"], config["TOURNAMENT_FACTOR_DEFAULT"]),
    (config["FACTOR_OPP_QUALITY"], config["OPP_QUALITY_FACTOR_DEFAULT"]),
    (config["FACTOR_SPECIAL_BOWL_TALENT"], config["BOWL_TALENT_DEFAULT"])
    ]

    df_bowl_agg = agg.add_wicketvalues(
        df, 
        rankings_config["WICKETS_AVG_COL"], 
        rankings_config["WICKETVALUE_COL"], 
        rankings_config["WICKETVALUE_AVG_COL"],
        rankings_config["PLAYER_ID"], 
        rankings_config["BOWLING_INNINGS_PLAYED"], 
        rankings_config["BALLS_BOWLED"], 
        rankings_config["WICKETS_COL"],
        rankings_config["RUNS_GIVEN"], 
        rankings_config["BOWLING_AVG_FACTOR"],
        rankings_config["BOWLING_AVG"],
        config["BOWLING_FACTOR_MIN"],
        config["BOWLING_FACTOR_MAX"],
        config["BASELINE_BOWLING_AVG"],
        config["FACTOR_BOWLING_AVG"],     
        bowling_factors,
        config  
    )

    df_bowl_rank = rank_t20.bowling_rankings(df_bowl_agg, rankings_config["WICKETVALUE_COL"], rankings_config["WICKETVALUE_AVG_COL"])

    # --- Map Player Names ---
    mapping_dict = dict(zip(player_mapping["Player ID"], player_mapping["Player Name"]))
    df_bat_rank["Player Name"] = df_bat_rank["Player ID"].map(mapping_dict)
    df_bowl_rank["Player Name"] = df_bowl_rank["Player ID"].map(mapping_dict)

    return df_bat_rank, df_bowl_rank