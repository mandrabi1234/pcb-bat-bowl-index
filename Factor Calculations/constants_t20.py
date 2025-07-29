
config = {
    # Factor Column Names
    "FACTOR_SR": "Factor_Runs_SR",
    "FACTOR_TOURNAMENT": "Factor_Runs_Tournament",
    "FACTOR_OPP_QUALITY": "Factor_Opp_Quality",
    "FACTOR_BAT_POSITION": "Factor_Batting_Position",
    "FACTOR_SPECIAL_BAT_TALENT": "Factor_Special_Batting_Talent",
    "FACTOR_SPECIAL_BOWL_TALENT": "Factor_Special_Bowling_Talent",
    "FACTOR_WICKETS_BATTER_POS_DISMISSED": "Factor_Wickets_Batter_Pos_Dismissed",
    "FACTOR_ECON_RATE": "Factor_Wickets_Economy_rate",

    # Strike Rate Scaling Constants
    "SR_FACTOR_DEFAULT": 1.0,
    "SR_BASELINE": 1.1,
    "SR_RANGE_MIN": 0.5,
    "SR_RANGE_MAX": 2.0,
    "SR_FACTOR_MIN": 0.85,
    "SR_FACTOR_MAX": 1.25,

    # Tournament Scaling Constants
    "TOURNAMENT_FACTOR_DEFAULT": 1.0,
    "TOURNAMENT_FACTOR_DICT": {
        "psl": 1.2,
        "champions t20": 1.0,
        "national t20": 0.8,
        "champions one day": 1.05,
        "president's cup one-day": 1.0,
        "qat": 1.05,
        "president's trophy grade-I": 1.0,
    },

    # Opposition Quality Scaling Constants
    "OPP_QUALITY_FACTOR_DEFAULT": 1.0,
    "OPP_QUALITY_RANKING_MAX_DIFF": 4.0,
    "OPP_QUALITY_FACTOR_MIN": 0.8,
    "OPP_QUALITY_FACTOR_MAX": 1.2,

    # Batting Position Scaling Constants
    "BATTING_POS_DEFAULT": 1.0,
    "POS_1_3": 0.95,
    "POS_4_5": 1.0,
    "POS_6_8": 1.05,
    "POS_9_11": 1.1,

    # Wicket Position Factors
    "WICKET_BAT_POS_DEFAULT": 1.0,
    "WICKET_BAT_POS_FACTOR_DICT": {
        0: 1.0,
        1: 1.1, 2: 1.1, 3: 1.1,
        4: 1.05, 5: 1.05,
        6: 1.0, 7: 1.0, 8: 1.0,
        9: 0.95, 10: 0.95, 11: 0.95,
    },

    # Bowling Economy Rate Constants
    "ECON_RATE_FACTOR_DEFAULT": 1.0,
    "ECON_RATE_BASELINE": 1.1,
    "ECON_RATE_RANGE_MIN": 0.8,
    "ECON_RATE_RANGE_MAX": 2.0,
    "ECON_RATE_FACTOR_MIN": 0.85,
    "ECON_RATE_FACTOR_MAX": 1.25,

    # Special Batting/Bowling Talent Constants
    "BAT_TALENT_SPECIAL": 1.1,
    "BOWL_TALENT_SPECIAL": 1.1,
    "BAT_TALENT_DEFAULT": 1.0,
    "BOWL_TALENT_DEFAULT": 1.0,

    # Player Averages Constants
    "FACTOR_BATTING_AVG": 1.0,
    "BASELINE_BATTING_AVG": 30,
    "FACTOR_BOWLING_AVG": 1.0,
    "BASELINE_BOWLING_AVG": 25

    # # Batting threshold
    # "MIN_RUNS": 200,
    # "RUNS_WEIGHT_BELOW_MIN": 0.80,

    # # Bowling threshold
    # "MIN_WICKETS": 20,
    # "WICKETS_WEIGHT_BELOW_MIN": 0.80


}
