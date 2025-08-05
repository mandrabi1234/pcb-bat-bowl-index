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

from constants_t20 import config as full_config
import copy

def generate_default_rankings(data_path, mapping_path, format_filter):
    """
    Generate default batting and bowling rankings using preset factor weights.
    
    Parameters:
        data_path (str): Path to the raw match data CSV.
        mapping_path (str): Path to the player mapping CSV.
        format_filter (str): Filter format (e.g., "t20", "list_a", "four_day").

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (batting_rankings_df, bowling_rankings_df)
    """
    # Normalize format_filter to a list
    if isinstance(format_filter, str):
        format_filter = [format_filter]

    # Determine config format
    if len(format_filter) == 1 and format_filter[0].lower() in full_config:
        selected_format = format_filter[0].lower()
        print(selected_format)
    else:
        selected_format = "t20"  # default fallback for multiple or unknown

    config = copy.deepcopy(full_config[selected_format])
    print("-------------CONFIG OUTPUT DEFAULT-------------\n", config)
    
    # Load and clean
    df = data_path
    player_mapping = mapping_path
    data_preprocessing(df)

    # Filter by match format
    df = df[df["Format"].str.lower().isin([fmt.lower() for fmt in format_filter])]

    # Loop through each selected format and collect qualifying Player IDs
    top_player_ids = set()

    # fmt_df = df[df["Format"] == fmt]

    top_bat_ids = (
        df.groupby("Player ID")["Runs Made"]
        .sum()
        .loc[lambda s: s >= 107]
        .sort_values(ascending=False)
        .head(60)
        .index
            )

    top_bowl_ids = (
        df.groupby("Player ID")["Wickets Taken"]
        .sum()
        .loc[lambda s: s >= 7]
        .sort_values(ascending=False)
        .head(60)
        .index
            )
    top_player_ids.update(set(top_bat_ids).union(set(top_bowl_ids)))

    # Final filter: keep only rows where Player ID is in top list
    df = df[df["Player ID"].isin(top_player_ids)].copy()
    print(df)
    
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
        config["BATTING_AVG_FACTOR"],
        batting_factors,
        config
    )

# Reattach 'Format' to aggregated batting and bowling data
    format_lookup = df[["Player ID", "Format"]].drop_duplicates(subset="Player ID")

    df_bat_agg = pd.merge(df_bat_agg, format_lookup, on="Player ID", how="left")

    # Re-filter the aggregated batting and bowling data based on format-specific thresholds

    bat_agg_filtered = []
    qualified_bat_ids = (
    df_bat_agg.groupby("Player ID")["Runs Made"]
    .sum()
    .loc[lambda s: s >= 107]
    .sort_values(ascending=False)
    .head(60)
    .index
    )
    bat_agg_filtered.append(df_bat_agg[df_bat_agg["Player ID"].isin(qualified_bat_ids)])


# Concatenate filtered results back into main DataFrames
    df_bat_agg = pd.concat(bat_agg_filtered, ignore_index=True)

    df_bat_rank = rank_t20.batting_rankings(df_bat_agg, rankings_config["RUNVALUE_COL"], rankings_config["RUNVALUE_AVG_COL"])
    max_score = df_bat_rank["Batting_Combined_Score"].max()
    df_bat_rank["Batting Score (Scaled 100)"] = (df_bat_rank["Batting_Combined_Score"] / max_score) * 100


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
        config["BOWLING_AVG_FACTOR"],     
        bowling_factors,
        config  
    )
    df_bowl_agg = pd.merge(df_bowl_agg, format_lookup, on="Player ID", how="left")

    bowl_agg_filtered = []

    qualified_bowl_ids = (
    df_bowl_agg.groupby("Player ID")["Wickets Taken"]
    .sum()
    .loc[lambda s: s >= 7]
    .sort_values(ascending=False)
    .head(60)
    .index
    )
    bowl_agg_filtered.append(df_bowl_agg[df_bowl_agg["Player ID"].isin(qualified_bowl_ids)])

    df_bowl_agg = pd.concat(bowl_agg_filtered, ignore_index=True)


    df_bowl_rank = rank_t20.bowling_rankings(df_bowl_agg, rankings_config["WICKETVALUE_COL"], rankings_config["WICKETVALUE_AVG_COL"])

    max_score = df_bowl_rank["Bowling_Combined_Score"].max()
    if max_score > 0:
        df_bowl_rank["Bowling Score (Scaled 100)"] = (df_bowl_rank["Bowling_Combined_Score"] / max_score) * 100
    else:
        df_bowl_rank["Bowling Score (Scaled 100)"] = 0


    # --- Map Player Names ---
    mapping_dict = dict(zip(player_mapping["Player ID"], player_mapping["Player Name"]))
    df_bat_rank["Player Name"] = df_bat_rank["Player ID"].map(mapping_dict)
    df_bowl_rank["Player Name"] = df_bowl_rank["Player ID"].map(mapping_dict)

    return df_bat_rank, df_bowl_rank