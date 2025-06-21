import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Factor Calculations')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Rankings')))

# Now these imports will work
from constants import *
from constants_t20 import *
import aggregations as agg 
import factors_t20 as ft20
import rankings_t20 as rank_t20
from data_cleaning import *

import streamlit as st
import pandas as pd
# import matplotlib.pyplot as plt
import numpy as np
import datetime
from datetime import date

st.set_page_config(layout="wide")


batting_data = pd.read_csv(r"C:\Users\mohia\Downloads\Rankings_UI_fully_dynamic_tabbed_downloadable\data\test_t20_rankings_bat_output2025-05-08.csv")
bowling_data = pd.read_csv(r"C:\Users\mohia\Downloads\Rankings_UI_fully_dynamic_tabbed_downloadable\data\test_t20_rankings_bowl_output2025-05-08.csv")

bowl_data = pd.DataFrame()
bowl_data["Player Name"] = bowling_data["Player Name"]
bowl_data["Player ID "] = bowling_data["Player ID"]
bowl_data["Bowling Score"] = bowling_data["Bowling_Combined_Score"]

bat_data = pd.DataFrame()
bat_data["Player Name"] = batting_data["Player Name"]
bat_data["Player ID "] = batting_data["Player ID"]
bat_data["Batting Score"] = batting_data["Batting_Combined_Score"]

# Sample data
df = pd.read_csv(r"C:\Users\mohia\Downloads\Rankings_UI_fully_dynamic_tabbed_downloadable\data\Filtered PCB Player Data - Final 582025.csv")
player_mapping = pd.read_csv(r"C:\Users\mohia\Downloads\Rankings_UI_fully_dynamic_tabbed_downloadable\data\player_mapping.csv")

data_preprocessing(df)

def player_map(df_map, df_input, player_name_col, player_id_col):
    id_to_name = pd.Series(df_map[player_name_col].values, index=df_map[player_id_col]).to_dict()
    df_input[player_name_col] = df_input[player_id_col].map(id_to_name)
    df_output = df_input.loc[:, [player_name_col] + [col for col in df_input.columns if col != player_name_col]]
    return df_output



# Function to filter and calculate results
def filter_and_calculate_bat(df_input,
                              sr_weight,
                              tournament_weight,
                              opp_weight,
                              bat_pos_weight,
                              spec_bat_talent_weight):  
    # Only keep T20 data
    df_input = df_input[df_input["Tournament"].isin(["psl", "champions t20", "national t20"])]

    # 🎯 Set individual factor scores
    ft20.strike_rate_factor(df_input, "Runs Made", "Balls Consumed", "Strike Rate Factor", sr_weight)
    ft20.tournament_calibre_factor(df_input, "Tournament", tournament_weight)
    ft20.opp_quality_factor(df_input, "Team Standing", "Opposition Standing", opp_weight)
    ft20.batting_position_factor(df_input, "Runs Made", "Batting Position", bat_pos_weight)
    ft20.special_bat_talent_factor(df_input, "Special Batting Talent", spec_bat_talent_weight)
    
    # 📊 Aggregate with factor weights
    batting_factor_columns = [
        ("Strike Rate Factor", sr_weight),
        ("Tournament Calibre Factor", tournament_weight),
        ("Opposition Quality Factor", opp_weight),
        ("Batting Position Factor", bat_pos_weight),
        ("Special Batting Talent Factor", spec_bat_talent_weight)
    ]

    df_bat_agg = agg.add_runvalues(
        df_input,
        RUN_AVG_COL, 
        RUNVALUE_COL,
        RUNVALUE_AVG_COL,
        BATTING_INNINGS_PLAYED,
        PLAYER_ID, 
        RUNS_MADE, 
        DISMISSED_COL,
        batting_factor_columns
    )

    # 🥇 Final Rankings
    df_bat_rank = rank_t20.batting_rankings(df_bat_agg, RUNVALUE_COL, RUNVALUE_AVG_COL)
    df_bat_rank = player_map(player_mapping, df_bat_rank, "Player Name", "Player ID")
    return df_bat_rank

# def filter_and_calculate_bat(df_input, SR_Factor, Tournament_Factor, Opponent_Factor, Bat_Pos_Factor, Special_Bat_Talent_Factor):  
#     # Only keep T20 data.
#     df_input = df_input[df_input["Tournament"].isin(["psl", "champions t20", "national t20"])]

#         # Set the SR factor.
#     ft20.strike_rate_factor(df_input, "Runs Made", "Balls Consumed", SR_Factor)

#         # Set the Tournament factor.
#     ft20.tournament_calibre_factor(df_input, "Tournament", Tournament_Factor)

#         # Set the Team Ranking diff (Opposition Quality) factor
#     ft20.opp_quality_factor(df_input, "Team Standing", "Opposition Standing", Opponent_Factor)

#         # Set the Batting Position Factor
#     ft20.batting_position_factor(df_input, "Runs Made", "Batting Position", Bat_Pos_Factor)

#         # Set the Special Batting Talent Factor
#     ft20.special_bat_talent_factor(df_input, "Special Batting Talent", Special_Bat_Talent_Factor)
        
#     batting_factor_columns = [
#         ("Strike Rate Factor", SR_Factor),
#         ("Tournament Calibre Factor", Tournament_Factor),
#         ("Opposition Quality Factor", Opponent_Factor),
#         ("Batting Position Factor", Bat_Pos_Factor),
#         ("Special Batting Talent Factor", Special_Bat_Talent_Factor)
#     ]
#     df_bat_agg = agg.add_runvalues(
#         df_input,
#         RUN_AVG_COL, 
#         RUNVALUE_COL,
#         RUNVALUE_AVG_COL,
#         BATTING_INNINGS_PLAYED,
#         PLAYER_ID, 
#         RUNS_MADE, 
#         DISMISSED_COL,
#         batting_factor_columns
#     )

#     df_bat_rank = rank_t20.batting_rankings(df_bat_agg, RUNVALUE_COL, RUNVALUE_AVG_COL)
#     df_bat_rank = player_map(player_mapping, df_bat_rank, "Player Name", "Player ID")
#     return df_bat_rank


# Function to filter and calculate results
def filter_and_calculate_bowl(df_input, Tournament_Factor, Opponent_Factor, Special_Bowling_Talent, Bowling_Factor, Wickets_Batter_Pos_Dismissed, Econ_Rate_Bowling):  
    # Only keep T20 data.
    df_input = df_input[df_input["Tournament"].isin(["psl", "champions t20", "national t20"])]

    
        #Set the Special Bowling Talent Factor
    ft20.special_bat_talent_factor(df_input, "Special Bowling Talent", Special_Bowling_Talent)

        #Batter dismissed factor.
    ft20.batters_dismissed_position_factor(df_input, "Wickets Taken", "Batters Dismissed", Wickets_Batter_Pos_Dismissed)

        #Economy Rate factor.
    ft20.economy_rate_factor(df_input, "Runs Given", "Balls Bowled", Econ_Rate_Bowling)

    bowling_factors = [Econ_Rate_Bowling, Wickets_Batter_Pos_Dismissed, Tournament_Factor, Opponent_Factor, Special_Bowling_Talent]
    df_bowl_agg = agg.add_wicketvalues(
        df_input, 
        WICKETS_AVG_COL, 
        WICKETVALUE_COL, 
        WICKETVALUE_AVG_COL, 
        PLAYER_ID, 
        BOWLING_INNINGS_PLAYED, 
        BALLS_BOWLED, 
        WICKETS_COL, 
        bowling_factors
    )
        # print(df_bowl_agg)

        # Bowling Rankings
    df_bowl_rank = rank_t20.bowling_rankings(df_bowl_agg, WICKETVALUE_COL, WICKETVALUE_AVG_COL)
    df_bowl_rank = player_map(player_mapping, df_bowl_rank, "Player Name", "Player ID")
    return df_bowl_rank


# Streamlit app
st.title("PCB Bat/Bowl Rankings Index")
# page_selection = st.radio("Select Rankings Type", ["Batting Rankings", "Bowling Rankings"])

# if page_selection == "Batting Rankings":
#     title = st.text_input("Filter View Name", help="Enter a name for the filtered view")
#     # rankingSelect = st.selectbox(
#     #     "What type of ranking would you like to generate?",
#     #     ("Batting", "Bowling"),
#     # )


#     # Initialize session state
#     if 'filtered_outputs' not in st.session_state:
#         st.session_state.filtered_outputs = []


#     # User inputs
#     st.subheader("General Weights")

#     col1, col2= st.columns(2)

#     with col1:
#         opp_weight = st.slider("Opponent Quality", 0.0, 5.0, 0.1)
#         filler = st.write("")
#     st.subheader("Batting Weights")
#     col3, col4, col5 = st.columns(3)

#     with col3:
#         sr_weight = st.slider("Strike Rate Factor", 0.0, 5.0, 0.1)
#     with col4:
#         spec_bat_talent_weight = st.slider("Special Batting Talent Weighting", 0.0, 5.0, 0.1)
#     with col5:
#         bat_pos_weight = st.slider("Batting Position Weighting", 0.0, 5.0, 0.1)

#     # st.subheader("Bowling Weights")

#     # col6, col7, col8, col9 = st.columns(4)
#     # with col6:
#     #     spec_bowl_talent_weight = st.slider("Special Bowling Talent Weighting", 0.0, 5.0, 0.1)
#     # with col7:
#     #     bowling_weight = st.slider("Bowling Weighting", 0.0, 5.0, 0.1)
#     # with col8:
#     #     bat_dismissal_pos_weight = st.slider("Batter Dismissal Position Weighting", 0.0, 5.0, 0.1)
#     # with col9:
#     #     econ_rate_weight = st.slider("Economy Rate Weighting", 0.0, 5.0, 0.1)
        
#     # Calculate button
#     if st.button("Calculate"):
#         filtered_df = filter_and_calculate_bat(df, page_selection, sr_weight, t20.TOURNAMENT_FACTOR_DICT, opp_weight, bat_pos_weight, spec_bat_talent_weight)
#         if len(st.session_state.filtered_outputs) < 5:
#             st.session_state.filtered_outputs.append({
#                 'title': title or f"Output {len(st.session_state.filtered_outputs) + 1}",
#                 'data': filtered_df
#             })
#         else:
#             st.warning("You can only store up to 5 filtered outputs.")

#     print(bat_data)

#     # Display results side by side
#     cols = st.columns(4)
#     with cols[0]:
#         st.dataframe(bat_data)

#     for i, output in enumerate(st.session_state.filtered_outputs):
#         with cols[i]:
#             st.subheader(output['title'])
#             st.dataframe(output['data'])

# if page_selection == "Bowling Rankings":
#     title = st.text_input("Filter View Name", help="Enter a name for the filtered view")
#     rankingSelect = st.selectbox(
#         "What type of ranking would you like to generate?",
#         ("Batting", "Bowling"),
#     )


#     # Initialize session state
#     if 'filtered_outputs' not in st.session_state:
#         st.session_state.filtered_outputs = []


#     # User inputs
#     st.subheader("General Weights")

#     col1, col2= st.columns(2)

#     with col1:
#         opp_weight = st.slider("Opponent Quality", 0.0, 5.0, 0.1)
#         filler = st.write("")
#     st.subheader("Batting Weights")
#     col3, col4, col5 = st.columns(3)

#     with col3:
#         sr_weight = st.slider("Strike Rate Factor", 0.0, 5.0, 0.1)
#     with col4:
#         spec_bat_talent_weight = st.slider("Special Batting Talent Weighting", 0.0, 5.0, 0.1)
#     with col5:
#         bat_pos_weight = st.slider("Batting Position Weighting", 0.0, 5.0, 0.1)

#     st.subheader("Bowling Weights")

#     col6, col7, col8, col9 = st.columns(4)
#     with col6:
#         spec_bowl_talent_weight = st.slider("Special Bowling Talent Weighting", 0.0, 5.0, 0.1)
#     with col7:
#         bowling_weight = st.slider("Bowling Weighting", 0.0, 5.0, 0.1)
#     with col8:
#         bat_dismissal_pos_weight = st.slider("Batter Dismissal Position Weighting", 0.0, 5.0, 0.1)
#     with col9:
#         econ_rate_weight = st.slider("Economy Rate Weighting", 0.0, 5.0, 0.1)
        
#     # Calculate button
#     if st.button("Calculate"):
#         filtered_df = filter_and_calculate_bowl(df, rankingSelect, sr_weight, opp_weight, spec_bowl_talent_weight, bowling_weight, bat_dismissal_pos_weight, econ_rate_weight)
#         if len(st.session_state.filtered_outputs) < 5:
#             st.session_state.filtered_outputs.append({
#                 'title': title or f"Output {len(st.session_state.filtered_outputs) + 1}",
#                 'data': filtered_df
#             })
#         else:
#             st.warning("You can only store up to 5 filtered outputs.")


#     # Display results side by side
#     cols = st.columns(4)
#     with cols[0]:
#         st.dataframe(bowl_data)
#     for i, output in enumerate(st.session_state.filtered_outputs):
#         with cols[i]:
#             st.subheader(output['title'])
#             st.dataframe(output['data'])

#         st.session_state.filtered_outputs = []

#         if len(st.session_state.filtered_outputs) < 5:
#             st.session_state.filtered_outputs.append({
#                 'title': title or f"Output {len(st.session_state.filtered_outputs) + 1}",
#                 'data': filtered_df
#             })
#         else:
#             st.warning("You can only store up to 5 filtered outputs.")




# === Dynamic weight inputs from user ===
# sr_weight = st.slider("Strike Rate Weight", 0.0, 1.0, 0.15)
# tournament_weight = st.slider("Tournament Weight", 0.0, 1.0, 0.15)
# opp_weight = st.slider("Opposition Weight", 0.0, 1.0, 0.15)
# bat_pos_weight = st.slider("Batting Position Weight", 0.0, 1.0, 0.15)
# spec_bat_talent_weight = st.slider("Special Batting Talent Weight", 0.0, 1.0, 0.4)



tab1, tab2 = st.tabs(["🏏 Batting Rankings", "🎯 Bowling Rankings"])

with tab1:
    st.session_state.filtered_outputs = []


    st.header("Batting Rankings")
    title = st.text_input("Filter View Name", help="Enter a name for the filtered view", key="filter_view_name_bat")

    options = st.multiselect(
    "Which formats would you like to include?", ["PSL", "T20", "First Class", "Test"], default = ["PSL", "T20"], label_visibility = "collapsed")

    sr_weight = st.slider("Strike Rate Weight", 0.0, 1.0, 0.15)
    tournament_weight = st.slider("Tournament Weight", 0.0, 1.0, 0.15)
    opp_weight = st.slider("Opposition Weight", 0.0, 1.0, 0.15)
    bat_pos_weight = st.slider("Batting Position Weight", 0.0, 1.0, 0.15)
    spec_bat_talent_weight = st.slider("Special Batting Talent Weight", 0.0, 1.0, 0.4)

    if st.button("Calculate Batting Rankings"):
        ranked_df = filter_and_calculate_bat(
            df, sr_weight, tournament_weight, opp_weight, bat_pos_weight, spec_bat_talent_weight
        )
        if len(st.session_state.filtered_outputs) < 5:
            st.session_state.filtered_outputs.append({
            'title': title or f"Output {len(st.session_state.filtered_outputs) + 1}",
            'data': ranked_df
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")
    # Display results side by side
    cols = st.columns(4)
    with cols[0]:
        st.dataframe(bat_data)
    for i, output in enumerate(st.session_state.filtered_outputs):
        with cols[i]:
            st.subheader(output['title'])
            st.dataframe(output['data'])


with tab2:

    st.session_state.filtered_outputs = []

    st.header("Bowling Rankings")
    title = st.text_input("Filter View Name", help="Enter a name for the filtered view",key="filter_view_name_bowl")

    eco_weight = st.slider("Economy Rate Weight", 0.0, 1.0, 0.25)
    avg_weight = st.slider("Bowling Average Weight", 0.0, 1.0, 0.25)
    wkts_weight = st.slider("Wickets Taken Weight", 0.0, 1.0, 0.25)
    spec_bowl_talent_weight = st.slider("Special Bowling Talent Weight", 0.0, 1.0, 0.25)

    if st.button("Calculate Bowling Rankings"):
        bowl_df = filter_and_calculate_bowl(
            df, eco_weight, avg_weight, wkts_weight, spec_bowl_talent_weight
        )
        if len(st.session_state.filtered_outputs) < 5:
            st.session_state.filtered_outputs.append({
            'title': title or f"Output {len(st.session_state.filtered_outputs) + 1}",
            'data': ranked_df
            })
        else:
            st.warning("You can only store up to 5 filtered outputs.")
    # Display results side by side
    cols = st.columns(4)
    with cols[0]:
        st.dataframe(bat_data)
    for i, output in enumerate(st.session_state.filtered_outputs):
        with cols[i]:
            st.subheader(output['title'])
            st.dataframe(output['data'])


