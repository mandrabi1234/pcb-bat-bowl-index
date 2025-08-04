import numpy as np
import pandas as pd


def add_runvalues(df, run_avg_col, runvalue_col, runvalue_avg_col, total_played_col, player_col, runs_col, dismissed_col, bat_avg_factor_col, bat_avg_col, bat_avg_min, bat_avg_max, bat_avg_bsln, bat_factor_avg, factor_cols, config):
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
    print(cols)
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
    df_filtered[runvalue_avg_col] = df_filtered[runvalue_col] / df_filtered[dismissed_col]
    df_filtered[run_avg_col] = df_filtered[runs_col] / df_filtered[dismissed_col]

    # Batting Average = Runs Made / Number of Dismissals
    df_filtered[bat_avg_col] = df_filtered[runs_col] / df_filtered[dismissed_col].replace(0, np.nan)

    # Normalize: lower average = better
    # Debug Notes: 
    df_filtered[bat_avg_factor_col] = df_filtered[bat_avg_col] / bat_avg_bsln
    df_filtered[bat_avg_factor_col] = df_filtered[bat_avg_factor_col].fillna(1.0)

    # Standardization of Values
    minVal = df_filtered[bat_avg_factor_col].min()
    maxVal = df_filtered[bat_avg_factor_col].max()
    factorMin = bat_avg_min
    factorMax = bat_avg_max

    df_filtered[bat_avg_factor_col] = (df_filtered[bat_avg_factor_col] - minVal) / (maxVal - minVal) 
    df_filtered[bat_avg_factor_col] = factorMin + (df_filtered[bat_avg_factor_col] * (factorMax - factorMin)) 
    
    # Multiply into existing weighted RunsValue
    df_filtered[runvalue_col] *= df_filtered[bat_avg_factor_col] * bat_factor_avg


    return df_filtered

def add_wicketvalues(df, wickets_avg_col, wicketvalue_col, wicketvalue_avg_col, player_col, total_played_col, balls_bowled, wickets_col, runs_given_col, bwl_avg_factor_col, bwl_avg_col, bwl_avg_min, bwl_avg_max, bwl_avg_bsln, bwl_factor_avg, factor_cols, config):
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

    df_filtered[wicketvalue_avg_col] = df_filtered[wicketvalue_col] / df_filtered[runs_given_col]
    df_filtered[wickets_avg_col] = df_filtered[wickets_col] / df_filtered[runs_given_col]

    # Bowling Average = Runs Given / Wickets Taken
    df_filtered[bwl_avg_col] = df_filtered[runs_given_col] / df_filtered[wickets_col].replace(0, np.nan)

    # Normalize: lower average = better
    
    df_filtered[bwl_avg_factor_col] = bwl_avg_bsln / df_filtered[bwl_avg_col]

    df_filtered[bwl_avg_col].replace([np.inf, -np.inf], 1, inplace=True)

    df_filtered[bwl_avg_factor_col] = df_filtered[bwl_avg_factor_col].fillna(1.0)

    # df_filtered["Bowling_Avg_Factor"] = 2.0
    # factorMin = 0.75
    # factorMax = 1.25
    df_filtered.loc[df_filtered[bwl_avg_factor_col] > bwl_avg_max, bwl_avg_factor_col] = bwl_avg_max
    df_filtered.loc[df_filtered[bwl_avg_factor_col] < bwl_avg_min, bwl_avg_factor_col] = bwl_avg_min
    
    # Standardize Values
    minVal = df_filtered[bwl_avg_factor_col].min()
    print("--Min Value--\n", minVal)
    maxVal = df_filtered[bwl_avg_factor_col].max()
    print("--Max Value--\n", maxVal)



    df_filtered[bwl_avg_factor_col] = (df_filtered[bwl_avg_factor_col] - minVal) / (maxVal - minVal) 
    df_filtered[bwl_avg_factor_col] = bwl_avg_min + (df_filtered[bwl_avg_factor_col] * (bwl_avg_max - bwl_avg_min)) 


    # Multiply into existing weighted WicketValue
    df_filtered[wicketvalue_col] *= df_filtered[bwl_avg_factor_col] * bwl_factor_avg

    return df_filtered
