config = {
  "t20": {
    "FACTOR_SR": "Factor_Runs_SR",
    "FACTOR_TOURNAMENT": "Factor_Runs_Tournament",
    "FACTOR_OPP_QUALITY": "Factor_Opp_Quality",
    "FACTOR_BAT_POSITION": "Factor_Batting_Position",
    "FACTOR_SPECIAL_BAT_TALENT": "Factor_Special_Batting_Talent",
    "FACTOR_SPECIAL_BOWL_TALENT": "Factor_Special_Bowling_Talent",
    "FACTOR_WICKETS_BATTER_POS_DISMISSED": "Factor_Wickets_Batter_Pos_Dismissed",
    "FACTOR_ECON_RATE": "Factor_Wickets_Economy_rate",

    "SR_FACTOR_DEFAULT": 1.0,
    "SR_BASELINE": 1.0,
    "SR_RANGE_MIN": 0.99,
    "SR_RANGE_MAX": 1.0,
    "SR_FACTOR_MIN": 0.99,
    "SR_FACTOR_MAX": 1.0,

    "BATTING_AVG_FACTOR": 1.0,
    "BASELINE_BATTING_AVG": 25.0,
    "BATTING_FACTOR_MIN": 0.99,
    "BATTING_FACTOR_MAX": 1.0,
    # "TOTAL_RUNS_WEIGHT": 50.0,
    # "AVERAGE_VALUE_RUNS_WEIGHT": 50.0,

    "BOWLING_AVG_FACTOR": 1.0,
    "BASELINE_BOWLING_AVG": 25.0,
    "BOWLING_FACTOR_MIN": 0.99,
    "BOWLING_FACTOR_MAX": 1.0,
    # "TOTAL_WICKETS_WEIGHT": 50.0,
    # "AVERAGE_VALUE_WICKETS_WEIGHT": 50.0,

    "TOURNAMENT_FACTOR_DEFAULT": 1.0,
    "TOURNAMENT_FACTOR_DICT": {
      "psl": 1.0,
      "cc t20": 1.0,
      "national t20": 1.0
    },

    "OPP_QUALITY_FACTOR_DEFAULT": 1.0,
    "OPP_QUALITY_RANKING_MAX_DIFF": 10.0,
    "OPP_QUALITY_FACTOR_MIN": 1.0,
    "OPP_QUALITY_FACTOR_MAX": 1.0,

    "BATTING_POS_DEFAULT": 1.0,
    "POS_1_3": 1.0,
    "POS_4_5": 1.0,
    "POS_6_8": 1.0,
    "POS_9_11": 1.0,

    "WICKET_BAT_POS_DEFAULT": 1.0,
    "WICKET_BAT_POS_FACTOR_DICT": {
      1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
      6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0
    },

    "ECON_RATE_FACTOR_DEFAULT": 1.0,
    "ECON_RATE_BASELINE": 1.0,
    "ECON_RATE_RANGE_MIN": 0.99,
    "ECON_RATE_RANGE_MAX": 1.0,
    "ECON_RATE_FACTOR_MIN": 0.99,
    "ECON_RATE_FACTOR_MAX": 1.0,

    "BAT_TALENT_DEFAULT": 1.0,
    "BAT_TALENT_SPECIAL": 1.0,
    "BOWL_TALENT_DEFAULT": 1.0,
    "BOWL_TALENT_SPECIAL": 1.0
  },

  "one_day": {
    "FACTOR_SR": "Factor_Runs_SR",
    "FACTOR_TOURNAMENT": "Factor_Runs_Tournament",
    "FACTOR_OPP_QUALITY": "Factor_Opp_Quality",
    "FACTOR_BAT_POSITION": "Factor_Batting_Position",
    "FACTOR_SPECIAL_BAT_TALENT": "Factor_Special_Batting_Talent",
    "FACTOR_SPECIAL_BOWL_TALENT": "Factor_Special_Bowling_Talent",
    "FACTOR_WICKETS_BATTER_POS_DISMISSED": "Factor_Wickets_Batter_Pos_Dismissed",
    "FACTOR_ECON_RATE": "Factor_Wickets_Economy_rate",

    "SR_FACTOR_DEFAULT": 1.0,
    "SR_BASELINE": 0.9,
    "SR_RANGE_MIN": 0.99,
    "SR_RANGE_MAX": 1.0,
    "SR_FACTOR_MIN": 0.99,
    "SR_FACTOR_MAX": 1.0,

    "BATTING_AVG_FACTOR": 1.0,
    "BASELINE_BATTING_AVG": 35.0,
    "BATTING_FACTOR_MIN": 0.99,
    "BATTING_FACTOR_MAX": 1.0,
    # "TOTAL_RUNS_WEIGHT": 50.0,
    # "AVERAGE_VALUE_RUNS_WEIGHT": 50.0,

    "BOWLING_AVG_FACTOR": 1.0,
    "BASELINE_BOWLING_AVG": 30.0,
    "BOWLING_FACTOR_MIN": 0.99,
    "BOWLING_FACTOR_MAX": 1.0,
    # "TOTAL_WICKETS_WEIGHT": 50.0,
    # "AVERAGE_VALUE_WICKETS_WEIGHT": 50.0,

    "TOURNAMENT_FACTOR_DEFAULT": 1.0,
    "TOURNAMENT_FACTOR_DICT": {
      "cc one day": 1.0,
      "president's cup one day": 1.0
    },

    "OPP_QUALITY_FACTOR_DEFAULT": 1.0,
    "OPP_QUALITY_RANKING_MAX_DIFF": 10.0,
    "OPP_QUALITY_FACTOR_MIN": 1.0,
    "OPP_QUALITY_FACTOR_MAX": 1.0,

    "BATTING_POS_DEFAULT": 1.0,
    "POS_1_3": 1.0,
    "POS_4_5": 1.0,
    "POS_6_8": 1.0,
    "POS_9_11": 1.0,

    "WICKET_BAT_POS_DEFAULT": 1.0,
    "WICKET_BAT_POS_FACTOR_DICT": {
      1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
      6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0
    },

    "ECON_RATE_FACTOR_DEFAULT": 1.0,
    "ECON_RATE_BASELINE": 1.0,
    "ECON_RATE_RANGE_MIN": 0.99,
    "ECON_RATE_RANGE_MAX": 1.0,
    "ECON_RATE_FACTOR_MIN": 0.99,
    "ECON_RATE_FACTOR_MAX": 1.0,

    "BAT_TALENT_DEFAULT": 1.0,
    "BAT_TALENT_SPECIAL": 1.0,
    "BOWL_TALENT_DEFAULT": 1.0,
    "BOWL_TALENT_SPECIAL": 1.0
  },

  "four_day": {
    "FACTOR_SR": "Factor_Runs_SR",
    "FACTOR_TOURNAMENT": "Factor_Runs_Tournament",
    "FACTOR_OPP_QUALITY": "Factor_Opp_Quality",
    "FACTOR_BAT_POSITION": "Factor_Batting_Position",
    "FACTOR_SPECIAL_BAT_TALENT": "Factor_Special_Batting_Talent",
    "FACTOR_SPECIAL_BOWL_TALENT": "Factor_Special_Bowling_Talent",
    "FACTOR_WICKETS_BATTER_POS_DISMISSED": "Factor_Wickets_Batter_Pos_Dismissed",
    "FACTOR_ECON_RATE": "Factor_Wickets_Economy_rate",

    "SR_FACTOR_DEFAULT": 1.0,
    "SR_BASELINE": 0.6,
    "SR_RANGE_MIN": 0.99,
    "SR_RANGE_MAX": 1.0,
    "SR_FACTOR_MIN": 0.99,
    "SR_FACTOR_MAX": 1.0,

    "BATTING_AVG_FACTOR": 1.0,
    "BASELINE_BATTING_AVG": 30.0,
    "BATTING_FACTOR_MIN": 0.99,
    "BATTING_FACTOR_MAX": 1.0,
    # "TOTAL_RUNS_WEIGHT": 50.0,
    # "AVERAGE_VALUE_RUNS_WEIGHT": 50.0,

    "BOWLING_AVG_FACTOR": 1.0,
    "BASELINE_BOWLING_AVG": 25.0,
    "BOWLING_FACTOR_MIN": 0.99,
    "BOWLING_FACTOR_MAX": 1.0,
    # "TOTAL_WICKETS_WEIGHT": 50.0,
    # "AVERAGE_VALUE_WICKETS_WEIGHT": 50.0,

    "TOURNAMENT_FACTOR_DEFAULT": 1.0,
    "TOURNAMENT_FACTOR_DICT": {
      "qea trophy": 1.0,
      "president's trophy grade i": 1.0
    },

    "OPP_QUALITY_FACTOR_DEFAULT": 1.0,
    "OPP_QUALITY_RANKING_MAX_DIFF": 10.0,
    "OPP_QUALITY_FACTOR_MIN": 1.0,
    "OPP_QUALITY_FACTOR_MAX": 1.0,

    "BATTING_POS_DEFAULT": 1.0,
    "POS_1_3": 1.0,
    "POS_4_5": 1.0,
    "POS_6_8": 1.0,
    "POS_9_11": 1.0,

    "WICKET_BAT_POS_DEFAULT": 1.0,
    "WICKET_BAT_POS_FACTOR_DICT": {
      1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
      6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0
    },

    "ECON_RATE_FACTOR_DEFAULT": 1.0,
    "ECON_RATE_BASELINE": 1.0,
    "ECON_RATE_RANGE_MIN": 0.99,
    "ECON_RATE_RANGE_MAX": 1.0,
    "ECON_RATE_FACTOR_MIN": 0.99,
    "ECON_RATE_FACTOR_MAX": 1.0,

    "BAT_TALENT_DEFAULT": 1.0,
    "BAT_TALENT_SPECIAL": 1.0,
    "BOWL_TALENT_DEFAULT": 1.0,
    "BOWL_TALENT_SPECIAL": 1.0
  }
}
