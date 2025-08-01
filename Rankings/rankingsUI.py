
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Factor Calculations')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Rankings')))

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
from generate_default_rankings import generate_default_rankings
import copy

# Create a runtime config editable by the UI
config = copy.deepcopy(default_config)


st.set_page_config(layout="wide")

# Set base directory to project root
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Path to the data folder
DATA_DIR = os.path.join(BASE_DIR, "data")

# Paste your own link here
spreadsheet_id = "18geKjHMU0ezmNvWDpngo8WWYNyumUJu2upTOblPEmHM"
gids = ["297170317", "947794568", "570966830"]

dfs = []
for i in range(len(gids)):
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gids[i]}"
    df = pd.read_csv(csv_url)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

print(df['Format'].unique())

mapping_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=1945069261"

player_mapping = pd.read_csv(mapping_url)
# Load data

batting_data, bowling_data = generate_default_rankings( df, player_mapping)


def move_column(df, col_name, new_index):
    col = df.pop(col_name)
    df.insert(new_index, col_name, col)
    return df

bowl_data = bowling_data
bowl_data = move_column(bowl_data, "Player Name", 0)
bowl_data = move_column(bowl_data, "Player ID", 1)

bat_data = batting_data
bat_data = move_column(bat_data, "Player Name", 0)
bat_data = move_column(bat_data, "Player ID", 1)

data_preprocessing(df)

def player_map(df_map, df_input, player_name_col, player_id_col):
    id_to_name = pd.Series(df_map[player_name_col].values, index=df_map[player_id_col]).to_dict()
    df_input[player_name_col] = df_input[player_id_col].map(id_to_name)
    df_output = df_input.loc[:, [player_name_col] + [col for col in df_input.columns if col != player_name_col]]
    return df_output

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
    title_bat = st.text_input("View Title", placeholder = "Please Input View Name", key="bat_title")


    # Map UI labels to actual dataset values
    format_map = {
        "T20": "t20",
        "ODI": "one_day",
        "Four Day": "four_day"
    }

        # Format selection and normalization
    format_select = st.multiselect(
        "Which format(s) would you like to include in your rankings?",
        options=["T20", "ODI", "Four Day"],
        default=["T20"]
    )

    # Normalize format selections
    selected_formats = [format_map[fmt] for fmt in format_select if fmt in format_map]
    
    # Ensure the data is normalized and filtered
    df["Format"] = df["Format"].str.lower()
    df = df[df["Format"].isin(selected_formats)]

    with st.sidebar.container():
        st.subheader("Batting Factors")
        with st.expander("Strike Rate"):
            config["SR_FACTOR_DEFAULT"] = st.slider("Strike Rate Default", 0.0, 1.0, 1.0, 0.05)
            config["SR_BASELINE"] = st.slider("Strike Rate Baseline", 0.0, 2.0, 1.1, 0.05)
            config["SR_RANGE_MIN"] = st.slider("Strike Rate Range Minimum", 0.0, 1.0, 0.5, 0.05)
            config["SR_RANGE_MAX"] = st.slider("Strike Rate Range Maximum", 0.0, 3.0, 2.0, 0.05)
            config["SR_FACTOR_MIN"] = st.slider("Strike Rate Factor Minimum", 0.0, 1.0, 0.85, 0.05)
            config["SR_FACTOR_MAX"] = st.slider("Strike Rate Factor Maximum", 0.0, 2.0, 1.25, 0.05)
        with st.expander("Average Factors"):
            config["FACTOR_BATTING_AVG"]= st.slider("Batting Average Factor", 0.0, 2.0, 1.0, .05)
            config["BASELINE_BATTING_AVG"]= st.slider("Baseline Batting Average", 0, 100, 25, 5)
            rankings_config["T20_BOWLING_RUNSVALUE_TOTAL_PROP"] = st.slider("Total Runs Value Weight", 0, 100, 60, 5)
            rankings_config["T20_BOWLING_RUNSVALUE_AVG_PROP"] = 100 - rankings_config["T20_BOWLING_RUNSVALUE_TOTAL_PROP"]

            st.markdown(f"Average Value Runs Weight: **{rankings_config["T20_BOWLING_RUNSVALUE_AVG_PROP"]}**")

        with st.expander("Tournament Factors"):
            config["TOURNAMENT_FACTOR_DEFAULT"] = st.slider("Tournament Factor Default", 0.0, 1.0, 1.0, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["psl"] = st.slider("PSL", 0.0, 2.0, 1.2, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["champions t20"] = st.slider("Champions Cup T20", 0.0, 2.0, 1.0, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["national t20"] = st.slider("National T20", 0.0, 1.0, 0.8, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["champions one day"] = st.slider("Champions ODI", 0.0, 2.0, 1.05, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["president's cup one-day"] = st.slider("President's Cup ODI", 0.0, 2.0, 1.0, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["qat"] = st.slider("QAT", 0.0, 2.0, 1.05, 0.05)
            config["TOURNAMENT_FACTOR_DICT"]["president's trophy grade-I"] = st.slider("President's Trophy Grade-I", 0.0, 2.0, 1.0, 0.05)
        
        with st.expander("Opponent Quality Factors"):
            config["OPP_QUALITY_FACTOR_DEFAULT"] = st.slider("Opponent Quality Default", 0.0, 2.0, 1.0, 0.1)
            config["OPP_QUALITY_MAX_RANK_DIFF"] = st.slider("Opp Quality Max Rank Diff", 0.0, 10.0, 4.0, 0.5)
            config["OPP_QUALITY_FACTOR_MIN"] = st.slider("Opp Quality Factor Min", 0.0, 1.0, 0.8, 0.05)
            config["OPP_QUALITY_FACTOR_MAX"] = st.slider("Opp Quality Factor Max", 0.0, 2.0, 1.2, 0.05)

        with st.expander("Batting Position Factors"):
            config["BATTING_POS_DEFAULT"] = st.slider("Batting Position Default", 0.0, 2.0, config["BATTING_POS_DEFAULT"], 0.05)
            config["POS_1_3"] = st.slider("Batting Position 1-3", 0.0, 2.0, config["POS_1_3"], 0.05)
            config["POS_4_5"] = st.slider("Batting Position 4-5", 0.0, 2.0, config["POS_4_5"], 0.05)
            config["POS_6_8"] = st.slider("Batting Position 6-8", 0.0, 2.0, config["POS_6_8"], 0.05)
            config["POS_9_11"] = st.slider("Batting Position 9-11", 0.0, 2.0, config["POS_9_11"], 0.05)

        with st.expander("Wicket Position Factors"):
            config["WICKET_BAT_POS_DEFAULT"] = st.slider("Wicket Position Default", 0.0, 2.0, config["WICKET_BAT_POS_DEFAULT"], 0.05)
            for i in range(1, 12):
                config["WICKET_BAT_POS_FACTOR_DICT"][i] = st.slider(f"Wicket Position {i}", 0.0, 2.0, config["WICKET_BAT_POS_FACTOR_DICT"][i], 0.05)


    with st.sidebar.container():
        st.subheader("Bowling Factors")
        with st.expander("Economy Rate Factors"): 
            config["ECON_RATE_FACTOR_DEFAULT"] = st.slider("Economy Rate Default", 0.0, 2.0, config["ECON_RATE_FACTOR_DEFAULT"], 0.05)
            config["ECON_RATE_BASELINE"] = st.slider("Economy Rate Baseline", 0.0, 2.0, config["ECON_RATE_BASELINE"], 0.05)
            config["ECON_RATE_RANGE_MIN"] = st.slider("Economy Rate Range Minimum", 0.0, 1.0, config["ECON_RATE_RANGE_MIN"], 0.05)
            config["ECON_RATE_RANGE_MAX"] = st.slider("Economy Rate Range Maximum", 0.0, 2.0, config["ECON_RATE_RANGE_MAX"], 0.05)
            config["ECON_RATE_FACTOR_MIN"] = st.slider("Economy Rate Factor Minimum", 0.0, 2.0, config["ECON_RATE_FACTOR_MIN"], 0.05)
            config["ECON_RATE_FACTOR_MAX"] = st.slider("Economy Rate Factor Maximum", 0.0, 2.0, config["ECON_RATE_FACTOR_MAX"], 0.05)
        with st.expander("Average Factors"):
            config["FACTOR_BOWLING_AVG"]= st.slider("Bowling Average Factor", 0.0, 2.0, 1.0, .05)
            config["BASELINE_BOWLING_AVG"]= st.slider("Baseline Bowling Average", 0, 100, 30, 5)
            rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"] = st.slider("Total Wickets Value Weight", 0, 100, 70, 5)
            rankings_config["T20_BOWLING_WICKETSVALUE_AVG_PROP"] = 100 - rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"]

            st.markdown(f"Average Value Wickets Weight: **{rankings_config["T20_BOWLING_WICKETSVALUE_AVG_PROP"]}**")



    with st.sidebar.container():
        st.subheader("Special Factors")
        with st.expander("Batting Talent"):
            config["BAT_TALENT_DEFAULT"] = st.slider("Batting Talent Default", 0.0, 2.0, 1.0, 0.1)
            config["BAT_TALENT_SPECIAL"] = st.slider("Special Batting Talent", 0.0, 2.0, 1.1, 0.1)

        with st.expander("Bowling Talent"):
            config["BOWL_TALENT_DEFAULT"] = st.slider("Bowling Talent Default", 0.0, 2.0, 1.0, 0.1)
            config["BOWL_TALENT_SPECIAL"] = st.slider("Special Bowling Talent", 0.0, 2.0, 1.1, 0.1)
    
    with st.sidebar.container():
        st.subheader("Format Factors")
        with st.expander(f"{format_select}"):
            rankings_config["T20_MIN_NUM_BATTING_INNINGS"] = st.slider("Minimum Batting Innings", 0.0, 100.0, 0.0, 1.0)
            rankings_config["T20_MIN_NUM_BOWLING_INNINGS"] = st.slider("Minimum Bowling Innings", 0.0, 100.0, 0.0, 1.0)
            rankings_config["T20_RUNS_MIN_PERCENTILE"] = st.slider("Minimum Runs Percentile", 0.0, 2.0, 0.1, 0.05)
            rankings_config["T20_RUNS_MAX_PERCENTILE"] = st.slider("Maximum Runs Percentile", 0.0, 2.0, 0.95, 0.05)
            rankings_config["T20_WICKETS_MIN_PERCENTILE"] = st.slider("Minimum Wickets Percentile", 0.0, 2.0, 0.2, 0.05)
            rankings_config["T20_WICKETS_MAX_PERCENTILE"] = st.slider("Maximum Wickets Percentile", 0.0, 2.0, 0.95, 0.05)


# Batting Factors Calculations

# Set the SR factor.
ft20.strike_rate_factor(df, "Runs Made", "Balls Consumed", config["FACTOR_SR"], config)

# Set the Tournament factor.
ft20.tournament_calibre_factor(df, "Tournament", config["FACTOR_TOURNAMENT"], config)

# Set the Team Ranking diff (Opposition Quality) factor
ft20.opp_quality_factor(df, "Team Standing", "Opposition Standing", config["FACTOR_OPP_QUALITY"], config)

# Set the Batting Position Factor
ft20.batting_position_factor(df, "Runs Made", "Batting Position", config["FACTOR_BAT_POSITION"], config)

# Set the Special Batting Talent Factor
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
    batting_factors,
    config
)

#Bowling Factors Calculations

## BOWLING
#Set the Special Bowling Talent Factor
ft20.special_bat_talent_factor(df, "Special Bowling Talent", config["FACTOR_SPECIAL_BOWL_TALENT"], config)

#Batter dismissed factor.
ft20.batters_dismissed_position_factor(df, "Wickets Taken", "Batters Dismissed", config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], config)

#Economy Rate factor.
ft20.economy_rate_factor(df, "Runs Given", "Balls Bowled", config["FACTOR_ECON_RATE"], config)

bowling_factors = [
    (config["FACTOR_ECON_RATE"], config["ECON_RATE_FACTOR_DEFAULT"]),
    (config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], config["WICKET_BAT_POS_DEFAULT"]),
    (config["FACTOR_TOURNAMENT"], config["TOURNAMENT_FACTOR_DEFAULT"]),
    (config["FACTOR_OPP_QUALITY"], config["OPP_QUALITY_FACTOR_DEFAULT"]),
    (config["FACTOR_BAT_POSITION"], config["BATTING_POS_DEFAULT"]),
    (config["FACTOR_SPECIAL_BOWL_TALENT"], config["BOWL_TALENT_DEFAULT"])
]

# bowling_factors = [config["FACTOR_ECON_RATE"], config["FACTOR_WICKETS_BATTER_POS_DISMISSED"], config["FACTOR_TOURNAMENT"], config["FACTOR_OPP_QUALITY"], config["FACTOR_SPECIAL_BOWL_TALENT"]]
# print("---Bowling Factors---\n", bowling_factors)
df_bowl_agg = agg.add_wicketvalues(
    df,
    rankings_config["WICKETS_AVG_COL"],
    rankings_config["WICKETVALUE_COL"],
    rankings_config["WICKETVALUE_AVG_COL"],
    rankings_config["PLAYER_ID"],
    rankings_config["BOWLING_INNINGS_PLAYED"],
    rankings_config["BALLS_BOWLED"],
    rankings_config["WICKETS_TAKEN"],
    rankings_config["RUNS_GIVEN"],       
    bowling_factors,
    config                               
)

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
        df_bat_rank["Batting Score"] = df_bat_rank["Batting_Combined_Score"]
        df_bat_rank = move_column(df_bat_rank, "Player Name", 0)
        df_bat_rank = move_column(df_bat_rank, "Player ID", 1)

        if len(st.session_state.bat_filtered_outputs) < 5:
            st.session_state.bat_filtered_outputs.append({
                'title': f"{title_bat} ({', '.join(format_select)})" or f"Output {len(st.session_state.bat_filtered_outputs) + 1} - {format_select} Data",
                'data': df_bat_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    with st.expander("Default Rankings", expanded=True):
        st.dataframe(bat_data)

    with st.container():
        st.write("User-Generated Rankings")
        for output in st.session_state.bat_filtered_outputs:
            with st.expander(output['title'], expanded=False):
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
        # print(df_bwl_rank)
        df_bwl_rank = player_map(player_mapping, df_bwl_rank, "Player Name", "Player ID")
        df_bwl_rank["Bowling Score"] = df_bwl_rank["Bowling_Combined_Score"]
        df_bwl_rank = move_column(df_bwl_rank, "Player Name", 0)
        df_bwl_rank = move_column(df_bwl_rank, "Player ID", 1)

        if len(st.session_state.bowl_filtered_outputs) < 5:
            st.session_state.bowl_filtered_outputs.append({
                'title': f"{title_bat} ({', '.join(format_select)})" or f"Output {len(st.session_state.bowl_filtered_outputs) + 1} - {format_select} Data",
                'data': df_bwl_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    with st.expander("Default Rankings", expanded=True):
        st.dataframe(bowl_data)
    
    with st.container():
        st.write("User-Generated Rankings")
        for output in st.session_state.bowl_filtered_outputs:
            with st.expander(output['title'], expanded=False):
                st.dataframe(output['data'])