import numpy as np
import pandas as pd


def add_runvalues(df, run_avg_col, runvalue_col, runvalue_avg_col, total_played_col, player_col, runs_col, dismissed_col, factor_cols):
    """Aggregate the "value of runs" for each player.

    Args:
        df: the filtered dataframe for a format.
        run_avg_col: the column name of the new raw runs average column.
        runvalue_col: the column name of the new runvalue column.
        runvalue_avg_col: the column name of the new runvalue average column.
        total_played_col: the column name of the new total innings played column.
        player_col: the column name for player ID.
        runs_col: the column name for (raw) runs made.
        dismissed_col: the column name for whether the player was dismissed.
        factor_cols: a list with column names for all factors.

    Returns:
        A dataframe which has columns:
            player_col, runs_col (summed), runvalue_col (summed), runvalue_avg_col, run_avg_col
    """
    cols = [col_name for col_name, _ in factor_cols] + [player_col, runs_col, dismissed_col]
    df_filtered = df[cols]
    df_filtered[runvalue_col] = df_filtered[runs_col]

    for col_name, weight in factor_cols:
        df_filtered[runvalue_col] *= df_filtered[col_name] * weight
    # Set total_played_col to 0 if Nan, else set to 1.
    df_filtered[total_played_col] =  np.where(df_filtered[runs_col].isna(), 0, 1)

    # Now group by and sum.
    cols_to_sum = [runs_col, runvalue_col, dismissed_col, total_played_col]
    df_filtered = df_filtered.groupby(player_col)[cols_to_sum].sum(numeric_only=True).reset_index()

    # If dismissed = 0 but total_played_col > 0, set dismissed = 1.0.
    df_filtered.loc[
        (df_filtered[dismissed_col] == 0.0) & (df_filtered[total_played_col] > 0.0), 
        dismissed_col] = 1.0
    
    # Also add the average columns.
    df_filtered[runvalue_avg_col] = df_filtered[runvalue_col] / df_filtered[total_played_col]
    df_filtered[run_avg_col] = df_filtered[runs_col] / df_filtered[total_played_col]


    return df_filtered


def add_wicketvalues(df, wickets_avg_col, wicketvalue_col, wicketvalue_avg_col, player_col, total_played_col, balls_bowled, wickets_col, runs_given_col, factor_cols, config):
    """Aggregate the value of wickets for each player and include bowling average."""
    cols = [col_name for col_name, _ in factor_cols] + [player_col, wickets_col, balls_bowled, runs_given_col]
    df_filtered = df[cols].copy()
    df_filtered[wicketvalue_col] = df_filtered[wickets_col]

    for col_name, weight in factor_cols:
        df_filtered[wicketvalue_col] *= df_filtered[col_name] * weight

    df_filtered[total_played_col] = np.where(
        (df_filtered[balls_bowled].isna() | (df_filtered[balls_bowled] == 0)), 0, 1
    )

    cols_to_sum = [wickets_col, wicketvalue_col, total_played_col, runs_given_col]
    df_filtered[wicketvalue_col] = pd.to_numeric(df_filtered[wicketvalue_col], errors='coerce')

    df_filtered = df_filtered.groupby(player_col)[cols_to_sum].sum(numeric_only=True).reset_index()

    df_filtered[wicketvalue_avg_col] = df_filtered[wicketvalue_col] / df_filtered[total_played_col]
    df_filtered[wickets_avg_col] = df_filtered[wickets_col] / df_filtered[total_played_col]

    # # 🔥 Bowling Average = Runs Given / Wickets Taken
    # df_filtered["Bowling_Avg"] = df_filtered[runs_given_col] / df_filtered[wickets_col].replace(0, np.nan)

    # # Normalize: lower average = better
    # df_filtered["Bowling_Avg_Factor"] = config["BASELINE_BOWLING_AVG"] / df_filtered["Bowling_Avg"]
    # df_filtered["Bowling_Avg_Factor"] = df_filtered["Bowling_Avg_Factor"].fillna(1.0)

    # # Multiply into existing weighted WicketValue
    # df_filtered[wicketvalue_col] *= df_filtered["Bowling_Avg_Factor"] * config["FACTOR_BOWLING_AVG"]

    return df_filtered
