
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

# bowl_data_input = os.path.join(DATA_DIR,"bowl_data.csv")
# bat_data_input = os.path.join(DATA_DIR,"bat_data.csv")

# batting_data = pd.read_csv(fr"{bat_data_input}")
# bowling_data = pd.read_csv(fr"{bowl_data_input}")
def move_column(df, col_name, new_index):
    col = df.pop(col_name)
    df.insert(new_index, col_name, col)
    return df

bowl_data = bowling_data
bowl_data = move_column(bowl_data, "Player Name", 0)
bowl_data = move_column(bowl_data, "Player ID", 1)

# bowl_data["Wickets Taken"] = bowling_data["Wickets Taken"]
# bowl_data["Bowling Score"] = bowling_data["Bowling_Combined_Score"]

bat_data = batting_data
bat_data = move_column(bat_data, "Player Name", 0)
bat_data = move_column(bat_data, "Player ID", 1)
print(bat_data)
# bat_data["Player Name"] = batting_data["Player Name"]
# bat_data["Player ID "] = batting_data["Player ID"]
# bat_data["Runs Made"] = batting_data["Runs Made"]
# bat_data["Batting Score"] = batting_data["Batting_Combined_Score"]

data_preprocessing(df)

def player_map(df_map, df_input, player_name_col, player_id_col):
    id_to_name = pd.Series(df_map[player_name_col].values, index=df_map[player_id_col]).to_dict()
    df_input[player_name_col] = df_input[player_id_col].map(id_to_name)
    df_output = df_input.loc[:, [player_name_col] + [col for col in df_input.columns if col != player_name_col]]
    return df_output

print("---Dismissal per Player---\n", df.groupby("Player ID")["Dismissed"].sum().reset_index())


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
            rankings_config["T20_BOWLING_RUNSVALUE_TOTAL_PROP"]= st.slider("Total Runs Value Weight", 0, 100, 40, 10)
            rankings_config["T20_BOWLING_RUNSVALUE_AVG_PROP"]= st.slider("Average Value Runs Weight", 0, 100, 60, 10)


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
            rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"]= st.slider("Total Wicket Value Weight", 0, 100, 30, 10)
            rankings_config["T20_BOWLING_WICKETSVALUE_AVG_PROP"]= st.slider("Average Value Wicket Weight", 0, 100, 70, 10)



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
            t20_min_bat_ins = st.slider("Minimum Batting Innings", 0.0, 10.0, 0.0, 1.0)
            t20_min_bwl_ins = st.slider("Minimum Bowling Innings", 0.0, 10.0, 0.0, 1.0)
            t20_run_val_prop = st.slider("Runs Value Total Prop", 0.0, 100.0, 60.0, 10.0)
            t20_run_avg_prop = st.slider("Runs Value Average Prop", 0.0, 100.0, 40.0, 10.0)
            t20_min_run_pctl = st.slider("Minimum Runs Percentile", 0.0, 2.0, 0.1, 0.05)
            t20_max_run_pctl = st.slider("Maximum Runs Percentile", 0.0, 2.0, 0.95, 0.05)




# Special Talents
# config["BAT_TALENT_DEFAULT"] = bat_talent_special_default
# config["BAT_TALENT_SPECIAL"] = bat_talent_special
# config["BOWL_TALENT_DEFAULT"] = bwl_talent_special_default
# config["BOWL_TALENT_SPECIAL"] = bwl_talent_special



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


# batting_factors = [
#     config["FACTOR_SR"],
#     config["FACTOR_TOURNAMENT"],
#     config["FACTOR_OPP_QUALITY"],
#     config["FACTOR_BAT_POSITION"],
#     config["FACTOR_SPECIAL_BAT_TALENT"]
# ]
print("---Batting Factors---\n", batting_factors)
print("---DataFrame---\n", df)
print("---Dismissal per Player---\n", df.groupby("Player ID")["Dismissed"].sum().reset_index())
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

# # Batting Average Factor
# df_bat_agg["Batting_Avg_Factor"] = df_bat_agg[rankings_config["RUN_AVG_COL"]] / config["BASELINE_BATTING_AVG"]
# print("--BATTING AVERAGE CHECK")
# print(df_bat_agg["Batting_Avg_Factor"])
# df_bat_agg["Batting_Avg_Factor"] = df_bat_agg["Batting_Avg_Factor"].fillna(1.0)
# df_bat_agg[rankings_config["RUNVALUE_COL"]] *= df_bat_agg["Batting_Avg_Factor"] * config["FACTOR_BATTING_AVG"]


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
print("---Bowling Factors---\n", bowling_factors)
df_bowl_agg = agg.add_wicketvalues(
    df,
    rankings_config["WICKETS_AVG_COL"],
    rankings_config["WICKETVALUE_COL"],
    rankings_config["WICKETVALUE_AVG_COL"],
    rankings_config["PLAYER_ID"],
    rankings_config["BOWLING_INNINGS_PLAYED"],
    rankings_config["BALLS_BOWLED"],
    rankings_config["WICKETS_TAKEN"],
    rankings_config["RUNS_GIVEN"],       # 🆕 New input column
    bowling_factors,
    config                               # 🆕 Pass entire config for factor use
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
        df_bat_rank["Batting Score"] = df_bat_rank["Batting_Combined_Score"]
        df_bat_rank = move_column(df_bat_rank, "Player Name", 0)
        df_bat_rank = move_column(df_bat_rank, "Player ID", 1)
        df_bat_rank = df_bat_rank.drop("Dismissed", axis=1)

        # df_bat_rank = df_bat_rank[['Player Name', 'Player ID', 'Runs Made',  'Batting Score']]
        if len(st.session_state.bat_filtered_outputs) < 5:
            st.session_state.bat_filtered_outputs.append({
                'title': title_bat or f"Output {len(st.session_state.bat_filtered_outputs) + 1}",
                'data': df_bat_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    with st.expander("Default Rankings", expanded=True):
        bat_data = bat_data.drop("Dismissed", axis=1)

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
        print(df_bwl_rank)
        df_bwl_rank = player_map(player_mapping, df_bwl_rank, "Player Name", "Player ID")
        df_bwl_rank["Bowling Score"] = df_bwl_rank["Bowling_Combined_Score"]
        df_bwl_rank = move_column(df_bwl_rank, "Player Name", 0)
        df_bwl_rank = move_column(df_bwl_rank, "Player ID", 1)
        # df_bwl_rank = df_bwl_rank[['Player Name', 'Player ID', 'Wickets Taken', 'Bowling Score']]

        if len(st.session_state.bowl_filtered_outputs) < 5:
            st.session_state.bowl_filtered_outputs.append({
                'title': title_bat or f"Output {len(st.session_state.bowl_filtered_outputs) + 1}",
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