import pandas as pd
import numpy as np

def overs_to_balls(overs):
    if pd.isna(overs):
        return 0
    try:
        if isinstance(overs, str):
            overs = overs.replace('*', '')
        overs = float(overs)
        whole = int(overs)
        fraction = int(round((overs - whole) * 10))
        return whole * 6 + fraction
    except Exception:
        return 0

def convert_if_decimal(val):
    try:
        if float(val) % 1 != 0:
            return overs_to_balls(val)
    except:
        pass
    return val  # leave unchanged if it's an integer or error


def data_preprocessing(df):
    
    # Convert overs to balls for four-day matches
    mask = df["Format"].str.lower() == "four_day"

    df.loc[mask, "Balls Bowled"] = df.loc[mask, "Balls Bowled"].apply(convert_if_decimal)
    # df.loc[mask, "Balls Bowled"] = df.loc[mask, "Balls Bowled"].apply(overs_to_balls)

    # Replace 'DNB', 'DNP', '*' with appropriate NaNs or zeros
    zero_map = {
        "Batters Dismissed": ["*", "N/a", "", "nan", "N0"],
        "Wickets Taken": ["*"],
        "Balls Bowled": ["DNB"],
        "Special Batting Talent": ["DNP"],
        "Special Bowling Talent": ["DNP"],
    }
    nan_map = {
        "Batters Dismissed": ["DNB", "DNP"],
        "Runs Given": ["DNB", "DNP"],
        "Wickets Taken": ["DNB", "DNP"],
        "Maidens Bowled": ["DNB", "DNP"],
        "Balls Bowled": ["DNP"],
    }

    for col, values in zero_map.items():
        df[col] = pd.to_numeric(df[col].replace(values, 0), errors='coerce').fillna(0)

    for col, values in nan_map.items():
        df[col] = df[col].replace(values, np.nan)

    # Safe numeric conversions
    df["Wickets Taken"] = pd.to_numeric(df["Wickets Taken"], errors="coerce").fillna(0).astype(int)
    df["Balls Bowled"] = pd.to_numeric(df["Balls Bowled"], errors="coerce").fillna(0).astype(int)
    df["Runs Given"] = pd.to_numeric(df["Runs Given"], errors="coerce").fillna(0).astype(int)

    # Clean and convert Runs Made
    df.loc[df["Runs Made"] == "DNB", "Runs Made"] = np.nan
    df["Runs Made"] = pd.to_numeric(df["Runs Made"].astype(str).str.replace("*", "", regex=False), errors="coerce")

    # Clean team and opposition standings
    for col in ["Team Standing", "Opposition Standing"]:
        df[col] = df[col].astype(str).str.extract(r"(\d+)").astype(float)

    # Ensure Batters Dismissed is stringified after cleaning
    df["Batters Dismissed"] = df["Batters Dismissed"].astype(str).replace("nan", "0")
    print(df["Dismissed"].unique())
    print(df["Balls Bowled"].unique())

    # Standardize case and strip whitespace
    df["Dismissed"] = df["Dismissed"].astype(str).str.strip().str.lower()

    # Define lowercased mappings
    dismissed_yes = [
        "yes", "yse", "ye", "y", "caught", "lbw", "runout", "run out", "bowled",
        "lwb", "hit wicket", "cuaght"
    ]

    dismissed_no = [
        "no", "did not", "not out", "retired hurt", "absent hurt", "did not play", "*",
        "dnp", "abnd", "abandoned", "retired", "dnb", "nan"
    ]

    # Apply mapping
    df["Dismissed"] = df["Dismissed"].where(~df["Dismissed"].isin(dismissed_no), 0)
    df["Dismissed"] = df["Dismissed"].where(~df["Dismissed"].isin(dismissed_yes), 1)

    # Anything else: treat as not dismissed (default to 0)
    df["Dismissed"] = pd.to_numeric(df["Dismissed"], errors="coerce").fillna(0).astype(int)

    print(df["Dismissed"].unique())
    # Special Batting Talent
    yes_vals = ["YES", "Yes", "yes", "yes "]
    no_vals = ["NO", "No", "no", "N0", ""]
    na_vals = [
        "DNB", "ABND", "*", "Abandoned", "Did Not Play", "Did not Play", "-", "N/a", "N/A", "n/a", "n/A"
    ]
    df["Special Batting Talent"] = df["Special Batting Talent"].replace(yes_vals, 1.0)
    df["Special Batting Talent"] = df["Special Batting Talent"].replace(no_vals, 0)
    df["Special Batting Talent"] = df["Special Batting Talent"].replace(na_vals, np.nan)
    df["Special Batting Talent"] = df["Special Batting Talent"].fillna(0).astype(float)

    # Balls Consumed
    df["Balls Consumed"] = df["Balls Consumed"].replace({
        "DNP": np.nan, "*": np.nan, "��7": np.nan, "ABSENT HURT": np.nan, "ABND": np.nan,
        "Retired Hurt": np.nan, "Time Out": np.nan, "Abandoned": np.nan, "Did Not Play": np.nan,
        "Did not Play": np.nan, "Did Not play": np.nan, "Did not play": np.nan, "-": np.nan,
        "N/a": np.nan, "N/A": np.nan, "n/a": np.nan, "n/A": np.nan, "No": np.nan
    })
    df["Balls Consumed"] = pd.to_numeric(df["Balls Consumed"].astype(str).str.replace("`", "", regex=False), errors="coerce")

    # Tournament cleanup
    df["Tournament"] = df["Tournament"].replace("", "Unknown").str.lower()
    df["Tournament"] = df["Tournament"].replace({
        r".*national[\s\-]?t[\-]?20.*": "national t20",
        r".*champions[\s\-]?t20.*": "champions t20",
        r".*psl.*": "psl"
    }, regex=True)

    # Special Bowling Talent
    df["Special Bowling Talent"] = df["Special Bowling Talent"].replace(yes_vals, 1.0)
    df["Special Bowling Talent"] = df["Special Bowling Talent"].replace(no_vals + ["", np.nan], 0)
    df["Special Bowling Talent"] = df["Special Bowling Talent"].replace(na_vals, np.nan)
    df["Special Bowling Talent"] = pd.to_numeric(df["Special Bowling Talent"], errors="coerce")

