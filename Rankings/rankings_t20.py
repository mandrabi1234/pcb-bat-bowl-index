import numpy as np
import pandas as pd

from constants import config as rankings_config
from constants_t20 import config as factor_config


def standardize_vals(df, col, new_col, min_percentile, max_percentile):
    
    val_min = df[col].quantile(min_percentile)
    val_max = df[col].quantile(max_percentile)
    val_range = val_max - val_min + 1e-9  
    # print(val_min, val_max, val_range)

    df[new_col] = df[col]
    # Set the floor.
    df.loc[df[new_col] < val_min, new_col] = val_min

    # Normalize
    df[new_col] = (df[new_col] - val_min) / val_range

    df[new_col] = df[new_col].clip(lower=0.05, upper=1.0)

    return df


def batting_rankings(df, runs_col, runs_avg_col):
    new_col_suffix = "_normed"
    new_runs_col = runs_col + new_col_suffix
    new_runs_avg_col = runs_avg_col + new_col_suffix

    df_filtered = df[
        df[rankings_config["BATTING_INNINGS_PLAYED"]]  # pull the column first
        >= rankings_config["T20_MIN_NUM_BATTING_INNINGS"]  # then compare
    ]

    # Standardize RunValues
    df_filtered = standardize_vals(
        df_filtered, runs_col, new_runs_col, rankings_config["T20_RUNS_MIN_PERCENTILE"], rankings_config["T20_RUNS_MAX_PERCENTILE"])
    
    # Standardize RunValues_AVG
    df_filtered = standardize_vals(
        df_filtered, runs_avg_col, new_runs_avg_col, rankings_config["T20_RUNS_MIN_PERCENTILE"], rankings_config["T20_RUNS_MAX_PERCENTILE"])
    
    df_filtered[rankings_config["BATTING_COMBINED_SCORE"]] = (
        (rankings_config["T20_BATTING_RUNSVALUE_TOTAL_PROP"] * df_filtered[new_runs_col])+
        (rankings_config["T20_BATTING_RUNSVALUE_AVG_PROP"] * df_filtered[new_runs_avg_col])
        # factor_weights.get("Factor_Runs_Per_Dismissal", 1.0) * df_filtered["Factor_Runs_Per_Dismissal"]
    )

    df_filtered[rankings_config["BATTING_RANKING"]] = df_filtered[rankings_config["BATTING_COMBINED_SCORE"]].rank(method='dense', ascending=False)
    df_filtered = df_filtered.set_index(rankings_config["BATTING_RANKING"]).sort_index()
    return df_filtered


def bowling_rankings(df, wickets_col, wickets_avg_col):

    new_col_suffix = "_normed"
    new_wick_col = wickets_col + new_col_suffix
    new_wick_avg_col = wickets_avg_col + new_col_suffix

    df_filtered = df[
        df[rankings_config["BOWLING_INNINGS_PLAYED"]]  # pull the column first
        >= rankings_config["T20_MIN_NUM_BOWLING_INNINGS"]  # then compare
    ]

    # Standardize WicketValues
    df_filtered = standardize_vals(
        df_filtered, wickets_col, new_wick_col, rankings_config["T20_WICKETS_MIN_PERCENTILE"], rankings_config["T20_WICKETS_MAX_PERCENTILE"])
    
    # Standardize WicketValues_AVG
    df_filtered = standardize_vals(
        df_filtered, wickets_avg_col, new_wick_avg_col, rankings_config["T20_WICKETS_MIN_PERCENTILE"], rankings_config["T20_WICKETS_MAX_PERCENTILE"])
    
    # Combine.
    df_filtered[rankings_config["BOWLING_COMBINED_SCORE"]] = (
        (rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"] * df_filtered[new_wick_col]) +
        (rankings_config["T20_BOWLING_WICKETSVALUE_AVG_PROP"] * df_filtered[new_wick_avg_col])
    )

    df_filtered[rankings_config["BOWLING_RANKING"]] = df_filtered[rankings_config["BOWLING_COMBINED_SCORE"]].rank(method='dense', ascending=False)
    df_filtered = df_filtered.set_index(rankings_config["BOWLING_RANKING"]).sort_index()
    return df_filtered