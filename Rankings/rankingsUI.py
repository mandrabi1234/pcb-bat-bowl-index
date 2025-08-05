
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

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] * {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)
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

df_default = pd.concat(dfs, ignore_index=True)


print(df['Format'].unique())

mapping_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=1945069261"

player_mapping = pd.read_csv(mapping_url)

def move_column(df, col_name, new_index):
    col = df.pop(col_name)
    df.insert(new_index, col_name, col)
    return df

def round_config_floats(d, decimals=4):
    for k, v in d.items():
        if isinstance(v, float):
            d[k] = round(v, decimals)
        elif isinstance(v, dict):
            round_config_floats(v, decimals)
    return d


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

#   ---Dynamic Format-Specfic Assignment---
    # Determine effective format (for single-format constants)
    if len(format_select) == 1:
        effective_format = format_map[format_select[0]]
    else:
        effective_format = "t20"  # Default for multi-format

    # Create a runtime config editable by the UI
    config = copy.deepcopy(default_config[effective_format])
    print("-----------Config Original-------------\n", config)

    config = round_config_floats(config)
    print("-----------Config Adjust-------------\n", config)
    # Normalize format selections
    selected_formats = [format_map[fmt] for fmt in format_select if fmt in format_map]

    # Ensure the data is normalized and filtered
    df["Format"] = df["Format"].str.lower()
    df = df[df["Format"].isin(selected_formats)]

    with st.sidebar.container():
        st.subheader("Batting Factors")
        with st.expander("Strike Rate"):
            config["SR_FACTOR_DEFAULT"] = st.slider("Strike Rate Default", 0.0, 1.0, config["SR_FACTOR_DEFAULT"], 0.0001, format="%.4f")
            config["SR_BASELINE"] = st.slider("Strike Rate Baseline", 0.0, 2.0, config["SR_BASELINE"], 0.0001, format="%.4f")
            config["SR_RANGE_MIN"] = st.slider("Strike Rate Range Minimum", 0.0, 1.0, config["SR_RANGE_MIN"], 0.0001, format="%.4f")
            config["SR_RANGE_MAX"] = st.slider("Strike Rate Range Maximum", 0.0, 3.0, config["SR_RANGE_MAX"], 0.0001, format="%.4f")
            config["SR_FACTOR_MIN"] = st.slider("Strike Rate Factor Minimum", 0.0, 1.0, config["SR_FACTOR_MIN"], 0.0001, format="%.4f")
            config["SR_FACTOR_MAX"] = st.slider("Strike Rate Factor Maximum", 0.0, 2.0, config["SR_FACTOR_MAX"], 0.0001, format="%.4f")
        with st.expander("Average Factors"):
            config["BATTING_AVG_FACTOR"]= st.slider("Batting Average Factor", 0.0, 2.0, config["BATTING_AVG_FACTOR"], 0.0001, format="%.4f")
            config["BASELINE_BATTING_AVG"]= st.slider("Baseline Batting Average", 0.0, 100.0, config["BASELINE_BATTING_AVG"], 5.0, format="%.4f")
            config["BATTING_FACTOR_MIN"]= st.slider("Batting Average Factor Min", 0.0, 2.00, config["BATTING_FACTOR_MIN"], 0.0001, format="%.4f")
            config["BATTING_FACTOR_MAX"]= st.slider("Batting Average Factor Max", 0.0, 2.00, config["BATTING_FACTOR_MAX"], 0.0001, format="%.4f")
            rankings_config["T20_BATTING_RUNSVALUE_TOTAL_PROP"] = st.slider("Total Runs Value Weight", 0.0, 100.0, rankings_config["T20_BATTING_RUNSVALUE_TOTAL_PROP"], 5.0, format="%.4f")
            rankings_config["T20_BATTING_RUNSVALUE_AVG_PROP"] = 100.0 - rankings_config["T20_BATTING_RUNSVALUE_TOTAL_PROP"]

            st.markdown(f"Average Value Runs Weight: **{rankings_config["T20_BATTING_RUNSVALUE_AVG_PROP"]}**")

        with st.expander("Tournament Factors"):
            config["TOURNAMENT_FACTOR_DEFAULT"] = st.slider("Tournament Factor Default", 0.0, 2.0, config["TOURNAMENT_FACTOR_DEFAULT"], 0.0001, format="%.4f")
            
            tournament_dict = config.get("TOURNAMENT_FACTOR_DICT", {})
            for tournament, default_val in tournament_dict.items():
                config["TOURNAMENT_FACTOR_DICT"][tournament] = st.slider(
                    f"{tournament.title()}", 0.0, 2.0, default_val, 0.01
                )

        # with st.expander("Tournament Factors"):
        #     config["TOURNAMENT_FACTOR_DEFAULT"] = st.slider("Tournament Factor Default", 0.0, 1.0, 1.0, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["psl"] = st.slider("PSL", 0.0, 2.0, 1.2, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["champions t20"] = st.slider("Champions Cup T20", 0.0, 2.0, 1.0, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["national t20"] = st.slider("National T20", 0.0, 1.0, 0.8, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["champions one day"] = st.slider("Champions ODI", 0.0, 2.0, 1.05, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["president's cup one-day"] = st.slider("President's Cup ODI", 0.0, 2.0, 1.0, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["qat"] = st.slider("QAT", 0.0, 2.0, 1.05, 0.05)
        #     config["TOURNAMENT_FACTOR_DICT"]["president's trophy grade-I"] = st.slider("President's Trophy Grade-I", 0.0, 2.0, 1.0, 0.05)
        
        with st.expander("Opponent Quality Factors"):
            config["OPP_QUALITY_FACTOR_DEFAULT"] = st.slider("Opponent Quality Default", 0.0, 2.0, config["OPP_QUALITY_FACTOR_DEFAULT"] , 0.1, format="%.4f")
            config["OPP_QUALITY_RANKING_MAX_DIFF"] = st.slider("Opp Quality Max Rank Diff", 0.0, 10.0, config["OPP_QUALITY_RANKING_MAX_DIFF"], 0.5, format="%.4f")
            config["OPP_QUALITY_FACTOR_MIN"] = st.slider("Opp Quality Factor Min", 0.0, 1.0, config["OPP_QUALITY_FACTOR_MIN"], 0.0001, format="%.4f")
            config["OPP_QUALITY_FACTOR_MAX"] = st.slider("Opp Quality Factor Max", 0.0, 2.0, config["OPP_QUALITY_FACTOR_MAX"], 0.0001, format="%.4f")

        with st.expander("Batting Position Factors"):
            config["BATTING_POS_DEFAULT"] = st.slider("Batting Position Default", 0.0, 2.0, config["BATTING_POS_DEFAULT"], 0.0001, format="%.4f")
            config["POS_1_3"] = st.slider("Batting Position 1-3", 0.0, 2.0, config["POS_1_3"], 0.0001, format="%.4f")
            config["POS_4_5"] = st.slider("Batting Position 4-5", 0.0, 2.0, config["POS_4_5"], 0.0001, format="%.4f")
            config["POS_6_8"] = st.slider("Batting Position 6-8", 0.0, 2.0, config["POS_6_8"], 0.0001, format="%.4f")
            config["POS_9_11"] = st.slider("Batting Position 9-11", 0.0, 2.0, config["POS_9_11"], 0.0001, format="%.4f")

        with st.expander("Wicket Position Factors"):
            config["WICKET_BAT_POS_DEFAULT"] = st.slider("Wicket Position Default", 0.0, 2.0, config["WICKET_BAT_POS_DEFAULT"], 0.0001, format="%.4f")
            for i in range(1, 12):
                config["WICKET_BAT_POS_FACTOR_DICT"][i] = st.slider(f"Wicket Position {i}", 0.0, 2.0, config["WICKET_BAT_POS_FACTOR_DICT"][i], 0.0001, format="%.4f")


    with st.sidebar.container():
        st.subheader("Bowling Factors")
        with st.expander("Economy Rate Factors"): 
            config["ECON_RATE_FACTOR_DEFAULT"] = st.slider("Economy Rate Default", 0.0, 2.0, config["ECON_RATE_FACTOR_DEFAULT"], 0.0001, format="%.4f")
            config["ECON_RATE_BASELINE"] = st.slider("Economy Rate Baseline", 0.0, 2.0, config["ECON_RATE_BASELINE"], 0.0001, format="%.4f")
            config["ECON_RATE_RANGE_MIN"] = st.slider("Economy Rate Range Minimum", 0.0, 1.0, config["ECON_RATE_RANGE_MIN"], 0.0001, format="%.4f")
            config["ECON_RATE_RANGE_MAX"] = st.slider("Economy Rate Range Maximum", 0.0, 2.0, config["ECON_RATE_RANGE_MAX"], 0.0001, format="%.4f")
            config["ECON_RATE_FACTOR_MIN"] = st.slider("Economy Rate Factor Minimum", 0.0, 2.0, config["ECON_RATE_FACTOR_MIN"], 0.0001, format="%.4f")
            config["ECON_RATE_FACTOR_MAX"] = st.slider("Economy Rate Factor Maximum", 0.0, 2.0, config["ECON_RATE_FACTOR_MAX"], 0.0001, format="%.4f")

        with st.expander("Average Factors"):
            config["BOWLING_AVG_FACTOR"] = st.slider("Bowling Average Factor", 0.0, 2.0, config["BOWLING_AVG_FACTOR"], 0.0001, format="%.4f")
            config["BASELINE_BOWLING_AVG"] = st.slider("Baseline Bowling Average", 0.0, 100.0, config["BASELINE_BOWLING_AVG"], 5.0, format="%.4f")
            config["BOWLING_FACTOR_MIN"]= st.slider("Bowling Average Factor Min", 0.0, 2.00, config["BOWLING_FACTOR_MIN"], 0.0001, format="%.4f")
            config["BOWLING_FACTOR_MAX"]= st.slider("Bowling Average Factor Max", 0.0, 2.00, config["BOWLING_FACTOR_MAX"], 0.0001, format="%.4f")
            rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"] = st.slider("Total Wickets Value Weight", 0.0, 100.0, rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"], 5.0, format="%.4f")
            rankings_config["T20_BOWLING_WICKETSVALUE_AVG_PROP"] = 100 - rankings_config["T20_BOWLING_WICKETSVALUE_TOTAL_PROP"]

            st.markdown(f"Average Value Wickets Weight: **{rankings_config["T20_BOWLING_WICKETSVALUE_AVG_PROP"]}**")



    with st.sidebar.container():
        st.subheader("Special Factors")
        with st.expander("Batting Talent"):
            config["BAT_TALENT_DEFAULT"] = st.slider("Batting Talent Default", 0.0, 2.0, config["BAT_TALENT_DEFAULT"], 0.1, format="%.4f")
            config["BAT_TALENT_SPECIAL"] = st.slider("Special Batting Talent", 0.0, 2.0, config["BAT_TALENT_SPECIAL"], 0.1, format="%.4f")

        with st.expander("Bowling Talent"):
            config["BOWL_TALENT_DEFAULT"] = st.slider("Bowling Talent Default", 0.0, 2.0, config["BOWL_TALENT_DEFAULT"], 0.1, format="%.4f")
            config["BOWL_TALENT_SPECIAL"] = st.slider("Special Bowling Talent", 0.0, 2.0, config["BOWL_TALENT_SPECIAL"], 0.1, format="%.4f")
    
    with st.sidebar.container():
        st.subheader("Format Factors")
        with st.expander(f"{format_select}"):
            rankings_config["T20_MIN_NUM_BATTING_INNINGS"] = st.slider("Minimum Batting Innings", 0.0, 100.0,  rankings_config["T20_MIN_NUM_BATTING_INNINGS"], 1.0, format="%.4f")
            rankings_config["T20_MIN_NUM_BOWLING_INNINGS"] = st.slider("Minimum Bowling Innings", 0.0, 100.0, rankings_config["T20_MIN_NUM_BOWLING_INNINGS"], 1.0, format="%.4f")
            rankings_config["T20_RUNS_MIN_PERCENTILE"] = st.slider("Minimum Runs Percentile", 0.0, 2.0,  rankings_config["T20_RUNS_MIN_PERCENTILE"], 0.0001, format="%.4f")
            rankings_config["T20_RUNS_MAX_PERCENTILE"] = st.slider("Maximum Runs Percentile", 0.0, 2.0, rankings_config["T20_RUNS_MIN_PERCENTILE"], 0.0001, format="%.4f")
            rankings_config["T20_WICKETS_MIN_PERCENTILE"] = st.slider("Minimum Wickets Percentile", 0.0, 2.0, rankings_config["T20_WICKETS_MIN_PERCENTILE"], 0.0001, format="%.4f")
            rankings_config["T20_WICKETS_MAX_PERCENTILE"] = st.slider("Maximum Wickets Percentile", 0.0, 2.0, rankings_config["T20_WICKETS_MAX_PERCENTILE"], 0.0001, format="%.4f")

format_minimums = {
        "t20": {"min_runs": 107, "min_wkts": 7, "top_bat": 60, "top_bowl": 60},
        "one_day": {"min_runs": 100, "min_wkts": 4, "top_bat": 50, "top_bowl": 50},
        "four_day": {"min_runs": 230, "min_wkts": 11, "top_bat": 100, "top_bowl": 80},
}

# Loop through each selected format and collect qualifying Player IDs
top_player_ids = set()
for fmt in selected_formats:
    thresholds = format_minimums.get(fmt, {})
    fmt_df = df[df["Format"] == fmt]

    top_bat_ids = (
        fmt_df.groupby("Player ID")["Runs Made"]
        .sum()
        .loc[lambda s: s >= thresholds["min_runs"]]
        .sort_values(ascending=False)
        .head(thresholds["top_bat"])
        .index
    )

    top_bowl_ids = (
        fmt_df.groupby("Player ID")["Wickets Taken"]
        .sum()
        .loc[lambda s: s >= thresholds["min_wkts"]]
        .sort_values(ascending=False)
        .head(thresholds["top_bowl"])
        .index
    )

    top_player_ids.update(set(top_bat_ids).union(set(top_bowl_ids)))

# Final filter: keep only rows where Player ID is in top list
df = df[df["Player ID"].isin(top_player_ids)].copy()

# Batting Factors Calculations
batting_data, bowling_data = generate_default_rankings( df, player_mapping, format_filter=selected_formats)

print("---Default Batting Rankings First Class---\n", batting_data)
bowling_data.to_csv(f"TEST OUTPUT ODI BOWLING 842025.csv", index=False)
batting_data.to_csv(f"TEST OUTPUT ODI BATTING 842025.csv", index=False)

bowl_data = bowling_data
bowl_data = move_column(bowl_data, "Player Name", 0)
bowl_data = move_column(bowl_data, "Player ID", 1)

bat_data = batting_data
bat_data = move_column(bat_data, "Player Name", 0)
bat_data = move_column(bat_data, "Player ID", 1)


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
    rankings_config["BATTING_AVG_FACTOR"],
    rankings_config["BATTING_AVG"],
    config["BATTING_FACTOR_MIN"],
    config["BATTING_FACTOR_MAX"],
    config["BASELINE_BATTING_AVG"],
    config["BATTING_AVG_FACTOR"],
    batting_factors,
    config
)
print("---Batting Aggregations---\n", df_bat_agg)
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
    rankings_config["BOWLING_AVG_FACTOR"],
    rankings_config["BOWLING_AVG"],
    config["BOWLING_FACTOR_MIN"],
    config["BOWLING_FACTOR_MAX"],
    config["BASELINE_BOWLING_AVG"],
    config["BOWLING_AVG_FACTOR"],     
    bowling_factors,
    config                               
)
# Reattach 'Format' to aggregated batting and bowling data
format_lookup = df[["Player ID", "Format"]].drop_duplicates(subset="Player ID")

df_bat_agg = pd.merge(df_bat_agg, format_lookup, on="Player ID", how="left")
df_bowl_agg = pd.merge(df_bowl_agg, format_lookup, on="Player ID", how="left")

# Re-filter the aggregated batting and bowling data based on format-specific thresholds

bat_agg_filtered = []
bowl_agg_filtered = []

for fmt in selected_formats:
    thresholds = format_minimums.get(fmt, {})
    
    # Filter batting data for this format
    fmt_bat = df_bat_agg[df_bat_agg["Format"] == fmt]
    qualified_bat_ids = (
        fmt_bat.groupby("Player ID")["Runs Made"]
        .sum()
        .loc[lambda s: s >= thresholds["min_runs"]]
        .sort_values(ascending=False)
        .head(thresholds["top_bat"])
        .index
    )
    bat_agg_filtered.append(fmt_bat[fmt_bat["Player ID"].isin(qualified_bat_ids)])

    # Filter bowling data for this format
    fmt_bowl = df_bowl_agg[df_bowl_agg["Format"] == fmt]
    qualified_bowl_ids = (
        fmt_bowl.groupby("Player ID")["Wickets Taken"]
        .sum()
        .loc[lambda s: s >= thresholds["min_wkts"]]
        .sort_values(ascending=False)
        .head(thresholds["top_bowl"])
        .index
    )
    bowl_agg_filtered.append(fmt_bowl[fmt_bowl["Player ID"].isin(qualified_bowl_ids)])

# Concatenate filtered results back into main DataFrames
df_bat_agg = pd.concat(bat_agg_filtered, ignore_index=True)
df_bowl_agg = pd.concat(bowl_agg_filtered, ignore_index=True)


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
        df_bat_rank = move_column(df_bat_rank, "Player Name", 0)
        df_bat_rank = move_column(df_bat_rank, "Player ID", 1)
        max_score = df_bat_rank["Batting_Combined_Score"].max()
        df_bat_rank["Batting Score (Scaled 100)"] = (df_bat_rank["Batting_Combined_Score"] / max_score) * 100


        print("Final Rankings Output---\n", df_bat_rank)
        if len(st.session_state.bat_filtered_outputs) < 5:
            st.session_state.bat_filtered_outputs.append({
                'title': f"{title_bat} ({', '.join(format_select)})" or f"Output {len(st.session_state.bat_filtered_outputs) + 1} - {format_select} Data",
                'data': df_bat_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    with st.expander(f"Default Rankings({', '.join(format_select)})", expanded=True):

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

        df_bwl_rank = player_map(player_mapping, df_bwl_rank, "Player Name", "Player ID")
        df_bwl_rank = move_column(df_bwl_rank, "Player Name", 0)
        df_bwl_rank = move_column(df_bwl_rank, "Player ID", 1)

        max_score = df_bwl_rank["Bowling_Combined_Score"].max()
        if max_score > 0:
            df_bwl_rank["Bowling Score (Scaled 100)"] = (df_bwl_rank["Bowling_Combined_Score"] / max_score) * 100
        else:
            df_bwl_rank["Bowling Score (Scaled 100)"] = 0

        if len(st.session_state.bowl_filtered_outputs) < 5:
            st.session_state.bowl_filtered_outputs.append({
                'title': f"{title_bat} ({', '.join(format_select)})" or f"Output {len(st.session_state.bowl_filtered_outputs) + 1} - {format_select} Data",
                'data': df_bwl_rank
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")

    # Display outputs side by side
    with st.expander(f"Default Rankings({', '.join(format_select)})", expanded=True):

        print(len(bowl_data))
        st.dataframe(bowl_data)
    
    with st.container():
        st.write("User-Generated Rankings")
        for output in st.session_state.bowl_filtered_outputs:
            with st.expander(output['title'], expanded=False):
                st.dataframe(output['data'])