
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Factor Calculations')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Rankings')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

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

# Create a runtime config editable by the UI
config = copy.deepcopy(default_config)


st.set_page_config(layout="wide")

# Set base directory to project root
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Path to the data folder
DATA_DIR = os.path.join(BASE_DIR, "data")

df_data_input = os.path.join(DATA_DIR, "Filtered PCB Player Data - Final 582025.csv")
player_map_input = os.path.join(DATA_DIR, "player_mapping.csv")
# Load data
bowl_data_input = os.path.join(DATA_DIR,"test_t20_rankings_bowl_output2025-05-08.csv")
bat_data_input = os.path.join(DATA_DIR,"test_t20_rankings_bat_output2025-05-08.csv")

batting_data = pd.read_csv(fr"{bat_data_input}")
bowling_data = pd.read_csv(fr"{bowl_data_input}")

bowl_data = pd.DataFrame()
bowl_data["Player Name"] = bowling_data["Player Name"]
bowl_data["Player ID "] = bowling_data["Player ID"]
bowl_data["Bowling Score"] = bowling_data["Bowling_Combined_Score"]

bat_data = pd.DataFrame()
bat_data["Player Name"] = batting_data["Player Name"]
bat_data["Player ID "] = batting_data["Player ID"]
bat_data["Batting Score"] = batting_data["Batting_Combined_Score"]

df = pd.read_csv(fr"{df_data_input}")
player_mapping = pd.read_csv(fr"{player_map_input}")

data_preprocessing(df)

def player_map(df_map, df_input, player_name_col, player_id_col):
    id_to_name = pd.Series(df_map[player_name_col].values, index=df_map[player_id_col]).to_dict()
    df_input[player_name_col] = df_input[player_id_col].map(id_to_name)
    df_output = df_input.loc[:, [player_name_col] + [col for col in df_input.columns if col != player_name_col]]
    return df_output



# def filter_and_calculate_bat(df_input, sr_weight, tournament_weight, opp_weight, bat_pos_weight, spec_bat_talent_weight):
#     df_input = df_input[df_input["Tournament"].isin(["psl", "champions t20", "national t20"])]
#     ft20.strike_rate_factor(df_input, "Runs Made", "Balls Consumed", "Strike Rate Factor", sr_weight)
#     ft20.tournament_calibre_factor(df_input, "Tournament", tournament_weight)
#     ft20.opp_quality_factor(df_input, "Team Standing", "Opposition Standing", opp_weight)
#     ft20.batting_position_factor(df_input, "Runs Made", "Batting Position", bat_pos_weight)
#     ft20.special_bat_talent_factor(df_input, "Special Batting Talent", spec_bat_talent_weight)
#     batting_factors = [
#         ("Strike Rate Factor", sr_weight),
#         ("Tournament Calibre Factor", tournament_weight),
#         ("Opposition Quality Factor", opp_weight),
#         ("Batting Position Factor", bat_pos_weight),
#         ("Special Batting Talent Factor", spec_bat_talent_weight)
#     ]
#     df_bat_agg = agg.add_runvalues(df_input, RUN_AVG_COL, RUNVALUE_COL, RUNVALUE_AVG_COL, BATTING_INNINGS_PLAYED,
#                                    PLAYER_ID, RUNS_MADE, DISMISSED_COL, batting_factors)
#     df_bat_rank = rank_t20.batting_rankings(df_bat_agg, RUNVALUE_COL, RUNVALUE_AVG_COL)
#     return player_map(player_mapping, df_bat_rank, "Player Name", "Player ID")

# def filter_and_calculate_bowl(df_input, econ_rate_weight, avg_weight, wkts_weight, spec_bowl_talent_weight):
#     df_input = df_input[df_input["Tournament"].isin(["psl", "champions t20", "national t20"])]
#     ft20.special_bat_talent_factor(df_input, "Special Bowling Talent", spec_bowl_talent_weight)
#     ft20.batters_dismissed_position_factor(df_input, "Wickets Taken", "Batters Dismissed", wkts_weight)
#     ft20.economy_rate_factor(df_input, "Runs Given", "Balls Bowled", econ_rate_weight)
#     bowling_factors = [econ_rate_weight, wkts_weight, avg_weight, avg_weight, spec_bowl_talent_weight]
#     df_bowl_agg = agg.add_wicketvalues(df_input, WICKETS_AVG_COL, WICKETVALUE_COL, WICKETVALUE_AVG_COL, PLAYER_ID,
#                                        BOWLING_INNINGS_PLAYED, BALLS_BOWLED, WICKETS_COL, bowling_factors)
#     df_bowl_rank = rank_t20.bowling_rankings(df_bowl_agg, WICKETVALUE_COL, WICKETVALUE_AVG_COL)


#     return player_map(player_mapping, df_bowl_rank, "Player Name", "Player ID")
st.markdown("""
    <style>
    /* Change font size of tab labels */
    [data-baseweb="tab"] {
        font-size: 60px !important;  /* Adjust to your desired size */
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("PCB Bat/Bowl Index")
st.link_button("Quick Reference Guide", "https://docs.google.com/document/d/1G8chnWg9rhQlv-lTN-8BEiKJqfwbVbatPzIj5VKAAR4/edit?usp=sharing")
tab1, tab2 = st.tabs(["🏏 Batting Rankings", "🎯 Bowling Rankings"])

with st.sidebar:
    st.markdown("### Filter View Names")
    title_bat = st.text_input("Batting View Title", placeholder = "Please Input View Name", key="bat_title")
    title_bowl = st.text_input("Bowling View Title", placeholder = "Please Input View Name", key="bowl_title")

    with st.sidebar.container():
        st.subheader("Batting Factors")
        with st.expander("Strike Rate"):
            sr_default = st.slider("Strike Rate Default", 0.0, 1.0, 1.0, 0.15)
            sr_baseline = st.slider("Strike Rate Baseline", 0.0, 2.0, 1.1, 0.15)
            sr_range_min = st.slider("Strike Rate Range Minimum", 0.0, 1.0, 0.5, 0.1)
            sr_range_max = st.slider("Strike Rate Range Maximum", 0.0, 3.0, 2.0, 0.25)
            sr_factor_min = st.slider("Strike Rate Factir Minimum", 0.0, 1.0, 0.85, 0.05)
            sr_factor_max = st.slider("Strike Rate Factor Maximum", 0.0, 2.0, 1.25, 0.25)

        with st.expander("Tournament Factors"):
            tourn_default = st.slider("Tournament Factor Default", 0.0, 1.0, 1.0, 0.1)
            psl_weight = st.slider("PSL", 0.0, 2.0, 1.2, 0.1)
            champ_t20 = st.slider("Champions Cup T20", 0.0, 2.0, 1.0, 0.1)
            nat_t20 = st.slider("National T20", 0.0, 1.0, 0.8, 0.1)
            champ_ODI = st.slider("Champions ODI", 0.0, 2.0, 1.05, 0.05)
            pres_ODI = st.slider("President's Cup ODI", 0.0, 2.0, 1.0, 0.1)
            qat = st.slider("QAT", 0.0, 2.0, 1.05, 0.05)
            pres_gradeI = st.slider("President's Trophy Grade-I", 0.0, 2.0, 1.0, 0.1)
        
        with st.expander("Opponent Quality Factors"):
            opp_quality_default = st.slider("Opponent Quality Default", 0.0, 2.0, 1.0, 0.1)
            opp_quality_max_diff = st.slider("Opponent Quality Maximum Ranking Difference", 0.0, 5.0, 4.0, 0.5)
            opp_quality_factor_min = st.slider("Opponent Quality Factor Minimum", 0.0, 1.0, 0.8, 0.1)
            opp_quality_factor_max = st.slider("Opponent Quality Factor Maximum", 0.0, 2.0, 1.2, 0.1)

        with st.expander("Batting Position Factors"):
            bat_pos_default = st.slider("Batting Position Default", 0.0, 1.0, 1.0, 0.1)
            pos_1_3 = st.slider("Batting Position 1-3", 0.0, 2.0, 0.95, 0.05)
            pos_4_5 = st.slider("Batting Position 4-5", 0.0, 2.0, 1.0, 0.05)
            pos_6_8 = st.slider("Batting Position 6-8", 0.0, 2.0, 1.05, 0.05)
            pos_9_11 = st.slider("Batting Position 9-11", 0.0, 2.0, 1.1, 0.05)

        with st.expander("Wicket Position Factors"):
            wkt_default = st.slider("Wicket Position Default", 0.0, 2.0, 1.0, 0.5)
            pos_1 = st.slider("Wicket Position 1", 0.0, 2.0, 1.1, 0.05)
            pos_2 = st.slider("Wicket Position 2", 0.0, 2.0, 1.1, 0.05)
            pos_3 = st.slider("Wicket Position 3", 0.0, 2.0, 1.1, 0.05)
            pos_4 = st.slider("Wicket Position 4", 0.0, 2.0, 1.05, 0.05)
            pos_5 = st.slider("Wicket Position 5", 0.0, 2.0, 1.05, 0.05)
            pos_6 = st.slider("Wicket Position 6", 0.0, 2.0, 1.0, 0.05)
            pos_7 = st.slider("Wicket Position 7", 0.0, 2.0, 1.0, 0.05)
            pos_8 = st.slider("Wicket Position 8", 0.0, 2.0, 1.0, 0.05)
            pos_9 = st.slider("Wicket Position 9", 0.0, 2.0, 0.95, 0.05)
            pos_10 = st.slider("Wicket Position 10", 0.0, 2.0, 0.95, 0.05)
            pos_11 = st.slider("Wicket Position 11", 0.0, 2.0, 0.95, 0.05)


    with st.sidebar.container():
        st.subheader("Bowling Factors")
        with st.expander("Economy Rate Factors"): 
            econ_rate = st.slider("Economy Rate Default", 0.0, 2.0, 1.0, 0.1)
            econ_rate_baseline = st.slider("Economy Rate Baseline", 0.0, 2.0, 1.1, 0.1)
            econ_rate_range_min = st.slider("Economy Rate Range Minimum", 0.0, 1.0, 0.8, 0.1)
            econ_rate_range_max = st.slider("Economy Rate Range Maximum", 0.0, 2.0, 2.0, 0.1)
            econ_rate_factor_min = st.slider("Economy Rate Factor Minimum", 0.0, 2.0, 0.85, 0.05)
            econ_rate_factor_max = st.slider("Economy Rate Factor Maximum", 0.0, 2.0, 1.25, 0.05)

    with st.sidebar.container():
        st.subheader("Special Factors")
        with st.expander("Batting Talent"):
            bat_talent_special_default = st.slider("Batting Talent Default", 0.0, 2.0, 1.0, 0.1)
            bat_talent_special = st.slider("Special Batting Talent", 0.0, 2.0, 1.1, 0.1)

        with st.expander("Bowling Talent"):
            bwl_talent_special_default = st.slider("Bowling Talent Default", 0.0, 2.0, 1.0, 0.1)
            bwl_talent_special = st.slider("Special Bowling Talent", 0.0, 2.0, 1.1, 0.1)
    
    with st.sidebar.container():
        st.subheader("Format Factors")
        with st.expander("T20"):
            t20_min_bat_ins = st.slider("T20 - Minimum Batting Innings", 0.0, 10.0, 5.0, 1.0)
            t20_min_bwl_ins = st.slider("T20 - Minimum Bowling Innings", 0.0, 10.0, 5.0, 1.0)
            t20_run_val_prop = st.slider("T20 - Runs Value Total Prop", 0.0, 100.0, 60.0, 10.0)
            t20_run_avg_prop = st.slider("T20 - Runs Value Average Prop", 0.0, 100.0, 40.0, 10.0)
            t20_min_run_pctl = st.slider("T20 - Minimum Runs Percentile", 0.0, 2.0, 0.1, 0.05)
            t20_max_run_pctl = st.slider("T20 - Maximum Runs Percentile", 0.0, 2.0, 0.95, 0.05)
# ✅ Populate runtime config from slider inputs

# Strike Rate
config["SR_FACTOR_DEFAULT"] = sr_default
config["SR_BASELINE"] = sr_baseline
config["SR_RANGE_MIN"] = sr_range_min
config["SR_RANGE_MAX"] = sr_range_max
config["SR_FACTOR_MIN"] = sr_factor_min
config["SR_FACTOR_MAX"] = sr_factor_max

# Tournament
config["TOURNAMENT_FACTOR_DEFAULT"] = tourn_default
config["TOURNAMENT_FACTOR_DICT"] = {
    "psl": psl_weight,
    "champions t20": champ_t20,
    "national t20": nat_t20,
    "champions one day": champ_ODI,
    "president's cup one-day": pres_ODI,
    "qat": qat,
    "president's trophy grade-I": pres_gradeI,
}

# Opponent Quality
config["OPP_QUALITY_FACTOR_DEFAULT"] = opp_quality_default
config["OPP_QUALITY_RANKING_MAX_DIFF"] = opp_quality_max_diff
config["OPP_QUALITY_FACTOR_MIN"] = opp_quality_factor_min
config["OPP_QUALITY_FACTOR_MAX"] = opp_quality_factor_max

# Batting Position
config["BATTING_POS_DEFAULT"] = bat_pos_default
config["POS_1_3"] = pos_1_3
config["POS_4_5"] = pos_4_5
config["POS_6_8"] = pos_6_8
config["POS_9_11"] = pos_9_11

# Wicket Position Factors
config["WICKET_BAT_POS_DEFAULT"] = wkt_default
config["WICKET_BAT_POS_FACTOR_DICT"] = {
    1: pos_1, 2: pos_2, 3: pos_3,
    4: pos_4, 5: pos_5, 6: pos_6,
    7: pos_7, 8: pos_8, 9: pos_9,
    10: pos_10, 11: pos_11,
}

# Economy Rate
config["ECON_RATE_FACTOR_DEFAULT"] = econ_rate
config["ECON_RATE_BASELINE"] = econ_rate_baseline
config["ECON_RATE_RANGE_MIN"] = econ_rate_range_min
config["ECON_RATE_RANGE_MAX"] = econ_rate_range_max
config["ECON_RATE_FACTOR_MIN"] = econ_rate_factor_min
config["ECON_RATE_FACTOR_MAX"] = econ_rate_factor_max

# Special Talents
config["BAT_TALENT_DEFAULT"] = bat_talent_special_default
config["BAT_TALENT_SPECIAL"] = bat_talent_special
config["BOWL_TALENT_DEFAULT"] = bwl_talent_special_default
config["BOWL_TALENT_SPECIAL"] = bwl_talent_special



# Batting Factors Calculations

# Set the SR factor.
ft20.strike_rate_factor(df, "Runs Made", "Balls Consumed", config["FACTOR_SR"])

# Set the Tournament factor.
ft20.tournament_calibre_factor(df, "Tournament", config["FACTOR_TOURNAMENT"])

# Set the Team Ranking diff (Opposition Quality) factor
ft20.opp_quality_factor(df, "Team Standing", "Opposition Standing", config["FACTOR_OPP_QUALITY"])

# Set the Batting Position Factor
ft20.batting_position_factor(df, "Runs Made", "Batting Position", config["FACTOR_BAT_POSITION"])

# Set the Special Batting Talent Factor
ft20.special_bat_talent_factor(df, "Special Batting Talent", config["FACTOR_SPECIAL_BAT_TALENT"])

batting_factors = [
    (config["FACTOR_SR"], sr_default),
    (config["FACTOR_TOURNAMENT"], tourn_default),
    (config["FACTOR_OPP_QUALITY"], opp_quality_default),
    (config["FACTOR_BAT_POSITION"], bat_pos_default),
    (config["FACTOR_SPECIAL_BAT_TALENT"], bat_talent_special)
]


# batting_factors = [
#     config["FACTOR_SR"],
#     config["FACTOR_TOURNAMENT"],
#     config["FACTOR_OPP_QUALITY"],
#     config["FACTOR_BAT_POSITION"],
#     config["FACTOR_SPECIAL_BAT_TALENT"]
# ]
print("---Batting Factors---\n", batting_factors)
df_bat_agg = agg.add_runvalues(
    df,
    rankings_config["RUN_AVG_COL"], 
    rankings_config["RUNVALUE_COL"],
    rankings_config["RUNVALUE_AVG_COL"],
    rankings_config["BATTING_INNINGS_PLAYED"],
    rankings_config["PLAYER_ID"], 
    rankings_config["RUNS_MADE"], 
    rankings_config["DISMISSED_COL"],
    batting_factors
)

#Bowling Factors Calculations

## BOWLING
#Set the Special Bowling Talent Factor
ft20.special_bat_talent_factor(df, "Special Bowling Talent", config["FACTOR_SPECIAL_BOWL_TALENT"])

#Batter dismissed factor.
ft20.batters_dismissed_position_factor(df, "Wickets Taken", "Batters Dismissed", config["FACTOR_WICKETS_BATTER_POS_DISMISSED"])

#Economy Rate factor.
ft20.economy_rate_factor(df, "Runs Given", "Balls Bowled", config["FACTOR_ECON_RATE"])

batting_factors = [
    (config["FACTOR_ECON_RATE"], econ_rate),
    (config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], bat_pos_default),
    (config["FACTOR_TOURNAMENT"], tourn_default),
    (config["FACTOR_OPP_QUALITY"], opp_quality_default),
    (config["FACTOR_BAT_POSITION"], bat_pos_default),
    (config["FACTOR_SPECIAL_BOWL_TALENT"], bwl_talent_special)
]

bowling_factors = [config["FACTOR_ECON_RATE"], config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], config["FACTOR_TOURNAMENT"], config["FACTOR_OPP_QUALITY"], config["FACTOR_SPECIAL_BOWL_TALENT"]]
df_bowl_agg = agg.add_wicketvalues(
    df, 
    rankings_config["WICKETS_AVG_COL"], 
    rankings_config["WICKETVALUE_COL"], 
    rankings_config["WICKETVALUE_AVG_COL"], 
    rankings_config["PLAYER_ID"], 
    rankings_config["BOWLING_INNINGS_PLAYED"], 
   rankings_config["BALLS_BOWLED"], 
    rankings_config["WICKETS_COL"], 
    bowling_factors
)
# print(df_bowl_agg)

# Bowling Rankings



with tab1:
    if 'bat_filtered_outputs' not in st.session_state:
        st.session_state.bat_filtered_outputs = []

    st.header("Batting Rankings")
    if st.button("Calculate Batting Rankings", key="bat"):
        df_bat_rank = rank_t20.batting_rankings(
            df_bat_agg,
            rankings_config["RUNVALUE_COL"],
            rankings_config["RUNVALUE_AVG_COL"]
        )
        df_bat_rank = player_map(player_mapping, df_bat_rank, "Player Name", "Player ID")
        if len(st.session_state.bat_filtered_outputs) < 5:
            st.session_state.bat_filtered_outputs.append({
                'title': title_bat or f"Output {len(st.session_state.bat_filtered_outputs) + 1}",
                'data': df_bat_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    cols = st.columns(min(1 + len(st.session_state.bat_filtered_outputs), 5))
    with cols[0]:
        st.subheader("DefaultData")
        st.dataframe(bat_data)

    for i, output in enumerate(st.session_state.bat_filtered_outputs, start=1):
        with cols[i]:
            st.subheader(output['title'])
            st.dataframe(output['data'])
with tab2:
    if 'bowl_filtered_outputs' not in st.session_state:
        st.session_state.bowl_filtered_outputs = []

    st.header("Bowling Rankings")
    if st.button("Calculate Bowling Rankings", key="bowl"):
        df_bwl_rank = rank_t20.bowling_rankings(
            df_bowl_agg,
            rankings_config["WICKETVALUE_COL"],
            rankings_config["WICKETVALUE_AVG_COL"]
        )
        df_bwl_rank = player_map(player_mapping, df_bwl_rank, "Player Name", "Player ID")
        if len(st.session_state.bowl_filtered_outputs) < 5:
            st.session_state.bowl_filtered_outputs.append({
                'title': title_bowl or f"Output {len(st.session_state.bowl_filtered_outputs) + 1}",
                'data': df_bwl_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    cols = st.columns(min(1 + len(st.session_state.bowl_filtered_outputs), 5))
    with cols[0]:
        st.subheader("Default Data")
        st.dataframe(bowl_data)

    for i, output in enumerate(st.session_state.bowl_filtered_outputs, start=1):
        with cols[i]:
            st.subheader(output['title'])
            st.dataframe(output['data'])
