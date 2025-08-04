import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'
pd.set_option('display.max_columns', None)

from constants_t20 import config as t20

# Compute the Strike Rate Factor for each (player, match, innings).
def strike_rate_factor(df, runs_made_col_name, balls_faced_col_name, sr_factor_col_name, config):

    # First set the Normalized Strike Rate:
    # Norm_SR =  (Runs Made / Balls Faced) * / SR_BASELINE
    df[sr_factor_col_name] = np.where(
        df[runs_made_col_name].isna() | df[balls_faced_col_name].isna(), 
        config["SR_FACTOR_DEFAULT"],
        (df[runs_made_col_name] / df[balls_faced_col_name]) / config["SR_BASELINE"]
    )

    # Now clip on the Min/Max.
    min_r = config["SR_RANGE_MIN"]
    max_r = config["SR_RANGE_MAX"]
    df.loc[df[sr_factor_col_name] < min_r, sr_factor_col_name] = min_r
    df.loc[df[sr_factor_col_name] > max_r, sr_factor_col_name] = max_r

    # Now scale to lie within the SR factor min/max in two steps:
    min_v = config["SR_FACTOR_MIN"]
    max_v = config["SR_FACTOR_MAX"]

    # Step 1: Scale to lie in range [0, 1]
    df[sr_factor_col_name] =  (df[sr_factor_col_name] - min_r) / (max_r - min_r)

    # Step 2: Scale to lie in range [min_v, max_v]
    df[sr_factor_col_name] =  (df[sr_factor_col_name] * (max_v - min_v)) + min_v


# Compute the Tournament Calibre Factor for each (player, match, innings).
def tournament_calibre_factor(df, tournament_col_name, tournament_factor_col_name, config):

    # Create a default column for Tournament Factor
    df[tournament_factor_col_name] = config["TOURNAMENT_FACTOR_DEFAULT"] 

    # Apply factors based on substring matching -  
    # The tournament naming conventions are not standardized across the board. This should bridge that gap
    for keyword, factor in config["TOURNAMENT_FACTOR_DICT"].items():
        df.loc[df["Tournament"].str.contains(keyword, case=False, na=False), tournament_factor_col_name] = factor



# Compute the Opposition Quality Factor for each (player, match, innings).
def opp_quality_factor(df, own_team_ranking, opposition_ranking, opp_quality_factor_col_name, config):

    # First set the ranking diffs. These need to be signed.
    # They are also normalized by the max range allowed.
    real_diff_allowed = 2 * config["OPP_QUALITY_RANKING_MAX_DIFF"]
    df[opp_quality_factor_col_name] = (config["OPP_QUALITY_RANKING_MAX_DIFF"] + df[own_team_ranking] - df[opposition_ranking]) / real_diff_allowed
    
    # Now normalize to lie in the factor's min/max range.
    factor_range = config["OPP_QUALITY_FACTOR_MAX"] - config["OPP_QUALITY_FACTOR_MIN"]
    df[opp_quality_factor_col_name] =  config["OPP_QUALITY_FACTOR_MIN"] + (df[opp_quality_factor_col_name] * factor_range)

    # Now clip on the Min/Max.
    df.loc[df[opp_quality_factor_col_name] < config["OPP_QUALITY_FACTOR_MIN"], opp_quality_factor_col_name] = config["OPP_QUALITY_FACTOR_MIN"]
    df.loc[df[opp_quality_factor_col_name] > config["OPP_QUALITY_FACTOR_MAX"], opp_quality_factor_col_name] = config["OPP_QUALITY_FACTOR_MAX"]

# Compute the batting position factor for each player (4 buckets- POS 1-3, 4-5, 6-8. 9-11)
def batting_position_factor(df, runs_made_col_name, batting_position_col_name, bat_pos_factor_col_name, config):
    
    df[bat_pos_factor_col_name] = config["BATTING_POS_DEFAULT"]

    df.loc[df[batting_position_col_name].isin([1, 2, 3]), bat_pos_factor_col_name] = config["POS_1_3"]
    df.loc[df[batting_position_col_name].isin([4, 5]), bat_pos_factor_col_name] = config["POS_4_5"]
    df.loc[df[batting_position_col_name].isin([6, 7, 8]), bat_pos_factor_col_name] = config["POS_6_8"]
    df.loc[df[batting_position_col_name].isin([9, 11]), bat_pos_factor_col_name] = config["POS_9_11"]

# Compute the batting position factor for each player (4 buckets- POS 1-3, 4-5, 6-8. 9-11)
def special_bat_talent_factor(df, special_bat_talent_col_name, special_bat_talent_factor_col_name, config):
    
    df[special_bat_talent_factor_col_name] = config["BAT_TALENT_DEFAULT"]

    df.loc[df[special_bat_talent_col_name] == 1.0, special_bat_talent_factor_col_name] = config["BAT_TALENT_SPECIAL"]

# Compute the bowling position factor for each player (4 buckets- POS 1-3, 4-5, 6-8. 9-11)
def special_bowl_talent_factor(df, special_bowl_talent_col_name, special_bowl_talent_factor_col_name, config):
    
    df[special_bowl_talent_factor_col_name] = config["BOWL_TALENT_DEFAULT"]

    df.loc[df[special_bowl_talent_col_name] == 1.0, special_bowl_talent_factor_col_name] = config["BOWL_TALENT_SPECIAL"]


# Compute factor for position of batters dismissed.
def batters_dismissed_position_factor(df, wickets_taken_col, batter_pos_col, batter_pos_dismissed_factor_col, config):

    # Create a default column for Batters Dismissed Factor
    df[batter_pos_dismissed_factor_col] = config["WICKET_BAT_POS_DEFAULT"] 

    # # Apply factors based on batting position
    # df[batter_pos_dismissed_factor_col] = np.where(
    #     df[wickets_taken_col] > 0,
    #     df[batter_pos_col].apply(
    #         lambda x: sum(config["WICKET_BAT_POS_FACTOR_DICT"][int(float(i))] for i in x.split(','))
    #         )/df[wickets_taken_col],
    #     config["WICKET_BAT_POS_DEFAULT"]
    # )


# Compute the Economy Rate Factor for each (player, match, innings).
def economy_rate_factor(df, runs_given_col, balls_bowled_col, econ_rate_factor_col, config):

    # First set the Normalized Economy Rate:
    # Norm_Econ_Rate =  (Runs Given / Balls Bowled) * / Econ_Rate_BASELINE
    df[econ_rate_factor_col] = np.where(
        df[runs_given_col].isna() | df[balls_bowled_col].isna(), 
        config["ECON_RATE_FACTOR_DEFAULT"],
        (df[runs_given_col] / df[balls_bowled_col]) / config["ECON_RATE_BASELINE"]
    )

    # Now clip on the Min/Max.
    min_r = config["ECON_RATE_RANGE_MIN"]
    max_r = config["ECON_RATE_RANGE_MAX"]
    df.loc[df[econ_rate_factor_col] < min_r, econ_rate_factor_col] = min_r
    df.loc[df[econ_rate_factor_col] > max_r, econ_rate_factor_col] = max_r

    # Now scale to lie within the Econ Rate factor min/max in two steps:
    min_v = config["ECON_RATE_FACTOR_MIN"]
    max_v = config["ECON_RATE_FACTOR_MAX"]

    # Step 1: Scale to lie in range [1, 0]
    df[econ_rate_factor_col] =  1 - (df[econ_rate_factor_col] - min_r) / (max_r - min_r)

    # Step 2: Scale to lie in range [min_v, max_v]
    df[econ_rate_factor_col] =  (df[econ_rate_factor_col] * (max_v - min_v)) + min_v

